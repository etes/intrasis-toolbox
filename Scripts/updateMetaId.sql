
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
        from "Definition" df, "SubClassDef" scdf
        where df."MetaId" = scdf."MetaId"
        and scdf."ClassId" = "classid"
        and df."Name" = "subclassname"
        and df."MetaId" = "subclassid";

    if not found then
     raise notice 'NOT_FOUND: SubClass % could not be found.', 
	    subclassname;
     return 'NOT_FOUND: SubClass ' || subclassname || ' with MetaId ' || subclassid || ' is not found.';
    else
        SELECT *
        INTO v_definition
        from "Definition" df
        where df."MetaId" = "new_metaid";

            if not found then
                -- Get tablespace used for the SubClass PRIMARY KEY
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
                
                raise notice 'UPDATED: SubClass % is found', rec."Name";
                return 'UPDATED: SubClass ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' is updated with new MetaId ' || "new_metaid";
            else
                raise notice 'EXISTS: MetaId % already exists', v_definition."MetaId";
                return 'EXISTS: MetaId ' || v_definition."MetaId" || ' already exists.';
            end if;
    end if;
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
        from "Definition" df, "ClassDef" cdf
        where df."MetaId" = cdf."MetaId"
        and df."Name" = "classname"
        and df."MetaId" = "classid";

    if not found then
     raise notice 'NOT_FOUND: Class % could not be found.', 
	    classname;
     return 'NOT_FOUND: Class ' || classname || ' with MetaId ' || classid || ' is not found.';
    else
        SELECT *
        INTO v_definition
        from "Definition" df
        where df."MetaId" = "new_metaid";

            if not found then
                -- Get tablespace used for the SubClass PRIMARY KEY
                SELECT constraint_catalog FROM information_schema.table_constraints
                    INTO tblspace
                    WHERE constraint_type = 'PRIMARY KEY' AND table_name = 'ClassDef';
                -- Remove Constraints
                ALTER TABLE "AttributeMember" DROP CONSTRAINT fk_attributemember_objectdef;
                ALTER TABLE "SymbolDef" DROP CONSTRAINT fk_symboldef_classdef;
                ALTER TABLE "RelationRule" DROP CONSTRAINT fk_relationrule_classdef;
                ALTER TABLE "RelationRule" DROP CONSTRAINT fk_relationrule_classdef1;
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
                
                raise notice 'UPDATED: Class % is found', rec."Name";
                return 'UPDATED: Class ' || rec."Name" || ' with MetaId ' || rec."MetaId" || ' is updated with new MetaId ' || "new_metaid";
            else
                raise notice 'EXISTS: MetaId % already exists', v_definition."MetaId";
                return 'EXISTS: MetaId ' || v_definition."MetaId" || ' already exists.';
            end if;
    end if;
COMMIT;
END $$;
