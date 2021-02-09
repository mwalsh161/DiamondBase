DELIMITER //

CREATE OR REPLACE PROCEDURE AddActionParamProc()
	MODIFIES SQL DATA
	SQL SECURITY INVOKER
	COMMENT 'To be executed (by trigger) if new parameter is assigned to an Action_Type'
BEGIN
	INSERT INTO sample_database_param_value_action (value, action_id, param_id) (
		SELECT IF(p.default_value IS NULL, '', p.default_value) AS value,
			a.id AS action_id,
			atp.param_id AS param_id
		FROM sample_database_action_type_params AS atp
				LEFT JOIN sample_database_param AS p ON atp.param_id = p.id,
			sample_database_action AS a
		WHERE atp.action_type_id = a.action_type_id AND
			(a.id, atp.param_id) NOT IN (
				SELECT a.id, pva.param_id
				FROM sample_database_param_value_action AS pva
					INNER JOIN sample_database_action_type_params AS atp ON pva.param_id = atp.param_id
					LEFT JOIN sample_database_action AS a ON pva.action_id = a.id
				WHERE a.action_type_id = atp.action_type_id
			)
	);
END//

CREATE OR REPLACE PROCEDURE AddDataParamProc()
	MODIFIES SQL DATA
	SQL SECURITY INVOKER
	COMMENT 'To be executed (by trigger) if new parameter is assigned to a Data_Type'
BEGIN
	INSERT INTO sample_database_param_value_data (value, data_id, param_id) (
		SELECT IF(p.default_value IS NULL, '', p.default_value) AS value,
			d.id AS data_id,
			dtp.param_id AS param_id
		FROM sample_database_data_type_params AS dtp
				LEFT JOIN sample_database_param AS p ON dtp.param_id = p.id,
			sample_database_data AS d
		WHERE dtp.data_type_id = d.data_type_id AND
			(d.id, dtp.param_id) NOT IN (
				SELECT d.id, pvd.param_id
				FROM sample_database_param_value_data AS pvd
					INNER JOIN sample_database_data_type_params AS dtp ON pvd.param_id = dtp.param_id
					LEFT JOIN sample_database_data AS d ON pvd.data_id = d.id
				WHERE d.data_type_id = dtp.data_type_id
			)
	);
END//

CREATE OR REPLACE TRIGGER AddActionParamInsertTrigger
	AFTER INSERT ON sample_database_action_type_params
	FOR EACH ROW
		CALL AddActionParamProc();

CREATE OR REPLACE TRIGGER AddActionParamUpdateTrigger
	AFTER UPDATE ON sample_database_action_type_params
	FOR EACH ROW
		CALL AddActionParamProc();

CREATE OR REPLACE TRIGGER AddDataParamInsertTrigger
	AFTER INSERT ON sample_database_data_type_params
	FOR EACH ROW
		CALL AddDataParamProc();

CREATE OR REPLACE TRIGGER AddDataParamUpdateTrigger
	AFTER UPDATE ON sample_database_data_type_params
	FOR EACH ROW
		CALL AddDataParamProc();

DELIMITER ;
