
CREATE OR REPLACE FUNCTION update_subclass_metaid(
    subclassid integer,
    classid integer,
    new_metaid integer,
    subclassname character varying,
    new_name character varying)
    RETURNS text
    LANGUAGE plpgsql
AS $$
DECLARE
    rec RECORD;
    v_definition "Definition"%rowtype;
    tblspace varchar;
BEGIN
    SELECT df."MetaId", scdf."ClassId", df."Name"
        INTO rec
        FROM "Definition" df, "SubClassDef" scdf
        WHERE df."MetaId" = scdf."MetaId"
        AND scdf."ClassId" = "classid"
        AND df."Name" = "subclassname"
        AND df."MetaId" = "subclassid";

    IF NOT FOUND THEN
     RETURN 'NOT_FOUND: SubClass ' || subclassname || ' with MetaId ' || subclassid || ' is not found.';
    ELSE
        SELECT *
        INTO v_definition
        FROM "Definition" df
        WHERE df."MetaId" = "new_metaid";

            IF NOT FOUND THEN
                -- Get tablespace used for the SubClassDef PRIMARY KEY
                SELECT constraint_catalog FROM information_schema.table_constraints
                    INTO tblspace
                    WHERE constraint_type = 'PRIMARY KEY' AND table_name = 'SubClassDef';
                -- Remove Constraints
                ALTER TABLE "DefinitionEventRel" DROP CONSTRAINT fk_definition_defintioneventrel;
                ALTER TABLE "AttributeMember" DROP CONSTRAINT fk_attributemember_objectdef;
                ALTER TABLE "Object" DROP CONSTRAINT fk_object_subclassdef;
                ALTER TABLE "ObjectDef" DROP CONSTRAINT fk_objectdef_definition;
                ALTER TABLE "SubClassDef" DROP CONSTRAINT "SubClassDef_pkey";
                ALTER TABLE "SubClassDef" DROP CONSTRAINT fk_subclassdef_classdef;
                ALTER TABLE "SubClassDef" DROP CONSTRAINT fk_subclassdef_objectdef;
                
                UPDATE "Definition" SET "MetaId" = "new_metaid", "Name" = "new_name"
                    WHERE "MetaId" = "subclassid" AND "Name" = "subclassname";
                
                UPDATE "SubClassDef" SET "MetaId" = "new_metaid"
                    WHERE "MetaId" = "subclassid";
                
                UPDATE "Object" SET "SubClassId" = "new_metaid"
                    WHERE "SubClassId" = "subclassid";
                
                UPDATE "ObjectDef" SET "MetaId" = "new_metaid"
                    WHERE "MetaId" = "subclassid";
                
                UPDATE "GeoObjectRule" SET "ObjectDefId" = "new_metaid"
                    WHERE "ObjectDefId" = "subclassid";
                
                UPDATE "AttributeMember" SET "ObjectDefId" = "new_metaid"
                    WHERE "ObjectDefId" = "subclassid";
                
                UPDATE "DefinitionEventRel" SET "DefinitionId" = "new_metaid"
                    WHERE "DefinitionId" = "subclassid";

                --Restore removed constaints
                EXECUTE 'ALTER TABLE "SubClassDef" ADD CONSTRAINT "SubClassDef_pkey" 
                            PRIMARY KEY ("MetaId") USING INDEX TABLESPACE "' || tblspace ||'";'
                USING tblspace;

                ALTER TABLE "SubClassDef" ADD CONSTRAINT fk_subclassdef_classdef FOREIGN KEY ("ClassId")
                        REFERENCES public."ClassDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "SubClassDef" ADD CONSTRAINT fk_subclassdef_objectdef FOREIGN KEY ("MetaId")
                        REFERENCES public."ObjectDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "Object" ADD CONSTRAINT fk_object_subclassdef FOREIGN KEY ("SubClassId")
                        REFERENCES public."SubClassDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "ObjectDef" ADD CONSTRAINT fk_objectdef_definition FOREIGN KEY ("MetaId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "AttributeMember" ADD CONSTRAINT fk_attributemember_objectdef FOREIGN KEY ("ObjectDefId")
                        REFERENCES public."ObjectDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "DefinitionEventRel" ADD CONSTRAINT fk_definition_defintioneventrel FOREIGN KEY ("DefinitionId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                
                RETURN 'UPDATED: SubClass ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' is updated with new MetaId ' || "new_metaid";
            ELSE
                RETURN 'EXISTS: MetaId ' || v_definition."MetaId" || ' already exists. SubClass ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' could not be updated.';
            END IF;
    END IF;
COMMIT;
END $$;

CREATE OR REPLACE FUNCTION update_class_metaid(
    classid integer,
    new_metaid integer,
    classname character varying,
    new_name character varying)
    RETURNS text
    LANGUAGE plpgsql
AS $$
DECLARE
    rec RECORD;
    v_definition "Definition"%rowtype;
    tblspace varchar;
BEGIN
    SELECT df."MetaId", df."Name"
        INTO rec
        FROM "Definition" df, "ClassDef" cdf
        WHERE df."MetaId" = cdf."MetaId"
        AND df."Name" = "classname"
        AND df."MetaId" = "classid";

    IF NOT FOUND THEN
     RETURN 'NOT_FOUND: Class ' || classname || ' with MetaId ' || classid || ' is not found.';
    ELSE
        SELECT *
        INTO v_definition
        FROM "Definition" df
        WHERE df."MetaId" = "new_metaid";

            IF NOT FOUND THEN
                -- Get tablespace used for the ClassDef PRIMARY KEY
                SELECT constraint_catalog FROM information_schema.table_constraints
                    INTO tblspace
                    WHERE constraint_type = 'PRIMARY KEY' AND table_name = 'ClassDef';
                -- Remove Constraints
                ALTER TABLE "DefinitionEventRel" DROP CONSTRAINT fk_definition_defintioneventrel;
                ALTER TABLE "AttributeMember" DROP CONSTRAINT fk_attributemember_objectdef;
                ALTER TABLE "SymbolDef" DROP CONSTRAINT fk_symboldef_classdef;
                ALTER TABLE "RelationRule" DROP CONSTRAINT fk_relationrule_classdef;
                ALTER TABLE "RelationRule" DROP CONSTRAINT fk_relationrule_classdef1;
                ALTER TABLE "GeoObjectRule" DROP CONSTRAINT fk_geoobjectrule_objectdef;
                ALTER TABLE "Object" DROP CONSTRAINT fk_object_classdef;
                ALTER TABLE "ObjectDef" DROP CONSTRAINT fk_objectdef_definition;
                ALTER TABLE "SubClassDef" DROP CONSTRAINT fk_subclassdef_classdef;
                ALTER TABLE "SubClassDef" DROP CONSTRAINT fk_subclassdef_objectdef;
                ALTER TABLE "ClassDef" DROP CONSTRAINT "ClassDef_pkey";
                --ALTER TABLE "ClassDef" DROP CONSTRAINT fk_classdef_attributedef;
                --ALTER TABLE "ClassDef" DROP CONSTRAINT fk_classdef_definition;
                ALTER TABLE "ClassDef" DROP CONSTRAINT fk_classdef_objectdef;
                
                UPDATE "Definition" SET "MetaId" = "new_metaid", "Name" = "new_name"
                    WHERE "MetaId" = "classid" AND "Name" = "classname";
                
                UPDATE "ClassDef" SET "MetaId" = "new_metaid"
                    WHERE "MetaId" = "classid";
                
                UPDATE "SubClassDef" SET "ClassId" = "new_metaid"
                    WHERE "ClassId" = "classid";
                
                UPDATE "Object" SET "ClassId" = "new_metaid"
                    WHERE "ClassId" = "classid";
                
                UPDATE "ObjectDef" SET "MetaId" = "new_metaid"
                    WHERE "MetaId" = "classid";
                
                UPDATE "GeoObjectRule" SET "ObjectDefId" = "new_metaid"
                    WHERE "ObjectDefId" = "classid";
                
                UPDATE "RelationRule" SET "ParentId" = "new_metaid"
                    WHERE "ParentId" = "classid";
                
                UPDATE "RelationRule" SET "ChildId" = "new_metaid"
                    WHERE "ChildId" = "classid";
                
                UPDATE "SymbolDef" SET "ClassId" = "new_metaid"
                    WHERE "ClassId" = "classid";
                
                UPDATE "AttributeMember" SET "ObjectDefId" = "new_metaid"
                    WHERE "ObjectDefId" = "classid";
                
                UPDATE "DefinitionEventRel" SET "DefinitionId" = "new_metaid"
                    WHERE "DefinitionId" = "classid";

                --Restore removed constaints
                EXECUTE 'ALTER TABLE "ClassDef" ADD CONSTRAINT "ClassDef_pkey" 
                            PRIMARY KEY ("MetaId") USING INDEX TABLESPACE "' || tblspace ||'";'
                USING tblspace;

                ALTER TABLE "ClassDef" ADD CONSTRAINT fk_classdef_objectdef FOREIGN KEY ("MetaId")
                        REFERENCES public."ObjectDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "SubClassDef" ADD CONSTRAINT fk_subclassdef_classdef FOREIGN KEY ("ClassId")
                        REFERENCES public."ClassDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "SubClassDef" ADD CONSTRAINT fk_subclassdef_objectdef FOREIGN KEY ("MetaId")
                        REFERENCES public."ObjectDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "Object" ADD CONSTRAINT fk_object_classdef FOREIGN KEY ("ClassId")
                        REFERENCES public."ClassDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "ObjectDef" ADD CONSTRAINT fk_objectdef_definition FOREIGN KEY ("MetaId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "GeoObjectRule" ADD CONSTRAINT fk_geoobjectrule_objectdef FOREIGN KEY ("ObjectDefId")
                        REFERENCES public."ObjectDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "RelationRule" ADD CONSTRAINT fk_relationrule_classdef FOREIGN KEY ("ChildId")
                        REFERENCES public."ClassDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "RelationRule" ADD CONSTRAINT fk_relationrule_classdef1 FOREIGN KEY ("ParentId")
                        REFERENCES public."ClassDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "SymbolDef" ADD CONSTRAINT fk_symboldef_classdef FOREIGN KEY ("ClassId")
                        REFERENCES public."ClassDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "AttributeMember" ADD CONSTRAINT fk_attributemember_objectdef FOREIGN KEY ("ObjectDefId")
                        REFERENCES public."ObjectDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "DefinitionEventRel" ADD CONSTRAINT fk_definition_defintioneventrel FOREIGN KEY ("DefinitionId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                
                RETURN 'UPDATED: Class ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' is updated with new MetaId ' || "new_metaid";
            ELSE
                RETURN 'EXISTS: MetaId ' || v_definition."MetaId" || ' already exists. Class ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' could not be updated.';
            END IF;
    END IF;
COMMIT;
END $$;

CREATE OR REPLACE FUNCTION update_relationtype_metaid(
    relationtypeid integer,
    new_metaid integer,
    relationtypename character varying,
    new_name character varying)
    RETURNS text
    LANGUAGE plpgsql
AS $$
DECLARE
    rec RECORD;
    v_definition "Definition"%rowtype;
    tblspace varchar;
BEGIN
    SELECT df."MetaId", df."Name"
        INTO rec
        FROM "Definition" df, "RelationTypeDef" rtdf
        WHERE df."MetaId" = rtdf."MetaId"
        AND df."Name" = "relationtypename"
        AND df."MetaId" = "relationtypeid";

    IF NOT FOUND THEN
     RETURN 'NOT_FOUND: RelationType ' || relationtypename || ' with MetaId ' || relationtypeid || ' is not found.';
    ELSE
        SELECT *
        INTO v_definition
        FROM "Definition" df
        WHERE df."MetaId" = "new_metaid";

            IF NOT FOUND THEN
                -- Get tablespace used for the RelationTypeDef PRIMARY KEY
                SELECT constraint_catalog FROM information_schema.table_constraints
                    INTO tblspace
                    WHERE constraint_type = 'PRIMARY KEY' AND table_name = 'RelationTypeDef';
                -- Remove Constraints
                ALTER TABLE "DefinitionEventRel" DROP CONSTRAINT fk_definition_defintioneventrel;
                ALTER TABLE "RelationDef" DROP CONSTRAINT fk_relationdef_relationtypedef;
                ALTER TABLE "RelationTypeDef" DROP CONSTRAINT "RelationTypeDef_pkey";
                ALTER TABLE "RelationTypeDef" DROP CONSTRAINT fk_relationtypedef_definition;
                
                UPDATE "Definition" SET "MetaId" = "new_metaid", "Name" = "new_name"
                    WHERE "MetaId" = "relationtypeid" AND "Name" = "relationtypename";
                
                UPDATE "RelationTypeDef" SET "MetaId" = "new_metaid", "Label" = "new_name"
                    WHERE "MetaId" = "relationtypeid";
                
                UPDATE "RelationDef" SET "RelationTypeDefId" = "new_metaid"
                    WHERE "RelationTypeDefId" = "relationtypeid";
                
                UPDATE "DefinitionEventRel" SET "DefinitionId" = "new_metaid"
                    WHERE "DefinitionId" = "relationtypeid";

                --Restore removed constaints
                EXECUTE 'ALTER TABLE "RelationTypeDef" ADD CONSTRAINT "RelationTypeDef_pkey" 
                            PRIMARY KEY ("MetaId") USING INDEX TABLESPACE "' || tblspace ||'";'
                USING tblspace;

                ALTER TABLE "RelationTypeDef" ADD CONSTRAINT fk_relationtypedef_definition FOREIGN KEY ("MetaId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "RelationDef" ADD CONSTRAINT fk_relationdef_relationtypedef FOREIGN KEY ("RelationTypeDefId")
                        REFERENCES public."RelationTypeDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "DefinitionEventRel" ADD CONSTRAINT fk_definition_defintioneventrel FOREIGN KEY ("DefinitionId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                
                RETURN 'UPDATED: RelationType ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' is updated with new MetaId ' || "new_metaid";
            ELSE
                RETURN 'EXISTS: MetaId ' || v_definition."MetaId" || ' already exists. RelationType ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' could not be updated.';
            END IF;
    END IF;
COMMIT;
END $$;


CREATE OR REPLACE FUNCTION update_relation_metaid(
    relationid integer,
    new_metaid integer,
    relationname character varying,
    new_name character varying)
    RETURNS text
    LANGUAGE plpgsql
AS $$
DECLARE
    rec RECORD;
    v_definition "Definition"%rowtype;
    tblspace varchar;
BEGIN
    SELECT df."MetaId", df."Name"
        INTO rec
        FROM "Definition" df, "RelationDef" rdf
        WHERE df."MetaId" = rdf."MetaId"
        AND df."Name" = "relationname"
        AND df."MetaId" = "relationid";

    IF NOT FOUND THEN
     RETURN 'NOT_FOUND: Relation ' || relationname || ' with MetaId ' || relationid || ' is not found.';
    ELSE
        SELECT *
        INTO v_definition
        FROM "Definition" df
        WHERE df."MetaId" = "new_metaid";

            IF NOT FOUND THEN
                -- Get tablespace used for the RelationDef PRIMARY KEY
                SELECT constraint_catalog FROM information_schema.table_constraints
                    INTO tblspace
                    WHERE constraint_type = 'PRIMARY KEY' AND table_name = 'RelationDef';
                -- Remove Constraints
                ALTER TABLE "DefinitionEventRel" DROP CONSTRAINT fk_definition_defintioneventrel;
                ALTER TABLE "ObjectRel" DROP CONSTRAINT fk_objectrel_relationdef;
                ALTER TABLE "RelationRule" DROP CONSTRAINT fk_relationrule_relationdef;
                ALTER TABLE "RelationDef" DROP CONSTRAINT "RelationDef_pkey";
                ALTER TABLE "RelationDef" DROP CONSTRAINT fk_relationdef_definition;
                
                UPDATE "Definition" SET "MetaId" = "new_metaid", "Name" = "new_name"
                    WHERE "MetaId" = "relationid" AND "Name" = "relationname";
                
                UPDATE "RelationDef" SET "MetaId" = "new_metaid"
                    WHERE "MetaId" = "relationid";
                
                UPDATE "RelationRule" SET "MetaId" = "new_metaid"
                    WHERE "MetaId" = "relationid";
                
                UPDATE "ObjectRel" SET "MetaId" = "new_metaid"
                    WHERE "MetaId" = "relationid";
                
                UPDATE "DefinitionEventRel" SET "DefinitionId" = "new_metaid"
                    WHERE "DefinitionId" = "relationid";

                --Restore removed constaints
                EXECUTE 'ALTER TABLE "RelationDef" ADD CONSTRAINT "RelationDef_pkey"
                            PRIMARY KEY ("MetaId") USING INDEX TABLESPACE "' || tblspace ||'";'
                USING tblspace;

                ALTER TABLE "RelationDef" ADD CONSTRAINT fk_relationdef_definition FOREIGN KEY ("MetaId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "RelationRule" ADD CONSTRAINT fk_relationrule_relationdef FOREIGN KEY ("MetaId")
                        REFERENCES public."RelationDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "ObjectRel" ADD CONSTRAINT fk_objectrel_relationdef FOREIGN KEY ("MetaId")
                        REFERENCES public."RelationDef" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                ALTER TABLE "DefinitionEventRel" ADD CONSTRAINT fk_definition_defintioneventrel FOREIGN KEY ("DefinitionId")
                        REFERENCES public."Definition" ("MetaId") MATCH SIMPLE
                        ON UPDATE NO ACTION
                        ON DELETE NO ACTION;
                
                RETURN 'UPDATED: Relation ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' is updated with new MetaId ' || "new_metaid";
            ELSE
                RETURN 'EXISTS: MetaId ' || v_definition."MetaId" || ' already exists. Relation ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' could not be updated.';
            END IF;
    END IF;
COMMIT;
END $$;

--DROP FUNCTION update_sequence(character varying,character varying,character varying);
CREATE OR REPLACE FUNCTION update_sequence(
	seq_name character varying,
	tbl_name character varying,
	col_name character varying)
	RETURNS text
	LANGUAGE plpgsql
AS $$
DECLARE
    old_last_val integer;
    new_last_val integer;
    max_val varchar;
BEGIN
    EXECUTE format('SELECT last_value from %s', seq_name) INTO old_last_val;
    -- Prevent concurrent insertions to the table while the sequence is being updated
    EXECUTE format('LOCK TABLE "%s" IN EXCLUSIVE MODE', tbl_name);
    -- Update the sequence's current value
    EXECUTE format('SELECT setval(''%s'', COALESCE(MAX("%s"), 1), MAX("%s") IS NOT null) FROM "%s";', 
        seq_name, col_name, col_name, tbl_name) INTO new_last_val;
    EXECUTE format('SELECT MAX("%s") FROM "%s"', col_name, tbl_name) INTO max_val;
    RETURN 'UPDATED: OLD_SQUENCE: ' || old_last_val || '; NEW_SEQUENCE: ' || new_last_val || '; MAX_MetaId: ' || max_val;
COMMIT;
END $$;
