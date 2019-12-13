from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone, dateparse
from django.core.urlresolvers import reverse
import hmac, hashlib, json, re, traceback, datetime

from slack.models import acidclean, failed_regex_strings
from sample_database.models import Sample, Action, Action_Type

class ParseError(Exception):
    pass

def validate_request(request):
    # verify auth https://api.slack.com/docs/verifying-requests-from-slack
    slack_signature = request.META.get('HTTP_X_SLACK_SIGNATURE',None)
    timestamp = request.META.get('HTTP_X_SLACK_REQUEST_TIMESTAMP',None)
    if not slack_signature or not timestamp:
        return False
    sig_basestring = 'v0:%s:%s'%(timestamp,request.body)
    digest = hmac.new(str(settings.SLACK_SIGNING_SECRET),sig_basestring,hashlib.sha256)
    signature = 'v0=' + digest.hexdigest()
    return hmac.compare_digest(signature,slack_signature)

# Slash command config can be found on slack's api page for this app:
# https://api.slack.com/apps/AHUKANHSQ/slash-commands

def parseacidclean(instructions,user):
    try:
        # Grab diamonds
        cropped_instructions = instructions
        diamonds = []
        p = re.compile(r'[, ]*?\"(.*)\"') # All things between quotes (grab the ", " if there for cropping)
        while True:
            match = p.search(cropped_instructions)
            if not match: break
            diamonds += match.group(1).replace('"','').split(',') # Remove quotes
            span = match.span()
            cropped_instructions = cropped_instructions[0:span[0]]+cropped_instructions[span[1]:]
        remaining_diamonds = re.findall(r'^(.*?)(?:(?<!,) |$)',cropped_instructions) # First space without a comma before it
        if len(remaining_diamonds) > 1: raise ParseError('Too many diamond list matches found!')
        if remaining_diamonds: # Now len(diamonds)==1 in the if block
            diamonds += [d.strip() for d in remaining_diamonds[0].split(',') if d.strip()]

        # Grab time and use django's more robust time parser
        time = re.findall(r'([0-9]*:[0-9]*[ ]?[aApPmM.]*)',instructions) # Two numbers with colon between them and am/pm after or with space between
        if len(time) > 1: raise ParseError('Too many time matches found!')
        if time:
            time_parsed = dateparse.parse_time(time[0])
            if not time_parsed: raise ParseError('Could not parse time: "%s"'%time)
            time = datetime.datetime.combine(datetime.date.today(),time_parsed)
            time.replace(tzinfo=timezone.get_current_timezone())
        else:
            time = timezone.now()

        # Grab temp if it is there
        temp = re.findall(r'((?<= )[0-9]*)[ ]?[C|c]?$',instructions) # Last number only if space before it
        if len(temp) > 1: raise ParseError('Too many temperature matches found!')
        if temp: # Keep consistent format
            try:
                temp = float(temp[0])
            except:
                raise ParseError('Failed to convert temperature "%s" to float'%temp[0])
        else:
            temp = None

        # Last thing is to swap diamonds strings to sample_database.models.Sample objects
        try:
            for i,sample in enumerate(diamonds):
                diamonds[i] = Sample.objects.get(name=sample)
        except Sample.DoesNotExist:
            raise Exception('Failed to find "%s" in diamondbase Samples'%sample)
    except:
        failed_regex_strings(string=instructions,user=user,error=traceback.format_exc()).save()
        raise
    return diamonds, time, temp

def in_acid(instructions,user,request):
    # Usage Hint: dmd1, dmd2 [at 12:45 PM]; 465 C
    [diamonds, time, temp] = parseacidclean(instructions,user)
    if not temp: raise Exception('You need to specify a temperature too!')
    clean = acidclean(temperature = temp, start_time = time,
                    issued_start_user = user, issued_start_time = timezone.now())
    clean.save()
    clean.diamonds.add(*diamonds)
    # Prepare response back
    url = request.build_absolute_uri(reverse('admin:slack_acidclean_change',args=(clean.id,)))
    highlight = '%s in on %s set to %g C'%(', '.join([str(d) for d in diamonds]), time.strftime('%A, %B %d %I:%M %p'),temp)
    assurance = 'Action will be created when completed.'
    edit_note = 'In the mean time, you can edit this temp URL %s.'%url
    attachment = {
        'fallback': '%s\n%s\n%s'%(highlight,assurance,edit_note),
        'pretext': highlight,
        'title': 'Acid clean started',
        'title_link': url,
        'text': assurance,
        'color':'good'
    }
    return attachment

def out_acid(instructions,user,request):
    # Usage Hint: [dmd1, dmd2] [at 12:45 PM]
    [diamonds, time, temp] = parseacidclean(instructions,user)
    cleans = acidclean.objects.filter(processed=False).order_by('-issued_start_time')
    if diamonds: # Get entry by diamonds (not sure if you can search on manytomany field)
        found = False
        for clean in cleans:
            names = zip(*clean.diamonds.values_list('name'))[0]
            if all([d.name in names for d in diamonds]):
                found = True
                break
        if not found: raise Exception('Could not find acid clean with: %s'%', '.join([d.name for d in diamonds]))
    else: # Get by most recent
        clean = cleans.first()
        if not clean: raise Exception('No acid clean started!')
    clean.stop_time = time
    clean.issued_stop_user = user
    clean.issued_stop_time = timezone.now()
    clean.save()

    url = request.build_absolute_uri(process_acid_clean(clean))
    highlight = '%s finished on %s.'%(', '.join([str(d) for d in clean.diamonds.all()]), time.strftime('%A, %B %d %I:%M %p'))
    assurance = 'Action created.'
    edit_note = 'You can view it here: %s'%url
    attachment = {
        'fallback': '%s\n%s\n%s'%(highlight,assurance,edit_note),
        'pretext': highlight,
        'title': 'Acid clean completed (add to notes)',
        'title_link': url,
        'text': assurance,
        'color':'good'
    }
    return attachment

def process_acid_clean(clean):
    # Take a slack.models.acidclean and generate a sample_database.models.Action
    duration = clean.stop_time - clean.start_time
    duration = '%i:%i'%(duration.seconds//3600,(duration.seconds//60)%60)
    action_type = Action_Type.objects.get(name='Acid Clean')
    new_acid_clean = Action(
        action_type=action_type,
        date=clean.start_time,
        fields='Tri-Acid\n%g\n%s'%(clean.temperature,duration),
        notes='%s issued start at %s and %s issued stop at %s.\nAdded from slack "diamondbase" app.'% \
            (clean.issued_start_user,clean.issued_start_time.strftime("%m/%d/%Y, %H:%M:%S"),
            clean.issued_stop_user,clean.issued_stop_time.strftime("%m/%d/%Y, %H:%M:%S"))
        )
    new_acid_clean.save()
    for sample in clean.diamonds.all():
        new_acid_clean.pieces.add(*sample.piece_set.all())
    if new_acid_clean.pieces.count() < 1:
        new_acid_clean.delete()
        raise Exception('No pieces in set of samples given (action not made)!')
    clean.processed = True
    clean.save()
    return reverse('DB:action_details',args=[clean.diamonds.first().name,clean.diamonds.first().piece_set.first().name,new_acid_clean.id])

@csrf_exempt
def slash_acidclean(request):
    if not validate_request(request): return HttpResponseForbidden()
    # Process command https://api.slack.com/slash-commands#app_command_handling
    msg_main = 'No Response :cry:'
    attachment = {'text':'This should not happen. Ask <@mpwalsh>.','color':'danger'}
    try:
        slack_command = request.POST.get('command',None)
        instructions = request.POST.get('text',None).strip()
        slack_user = request.POST.get('user_name',request.POST.get('user_id',''))
        if slack_command == '/in-acid':
            attachment = in_acid(instructions,slack_user,request)
            msg_main = 'in-acid'
        elif slack_command == '/out-acid':
            attachment = out_acid(instructions,slack_user,request)
            msg_main = 'out-acid'
        else:
            raise Http404('Unsupported slash command for diamondbase app')
    except Exception as err:
        msg_main = '%s :cry:: %s'%(type(err).__name__,err.message)
        attachment = {'text':'%s\n\nContact <@mpwalsh> for help!'%traceback.format_exc(),'color':'danger'}
    reply = {
        "response_type": "in_channel",
        "text": msg_main,
        'attachments':[]
    }
    if attachment:
        reply['attachments'].append(attachment)
    return JsonResponse(reply)
