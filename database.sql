BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "etiquettes" (
	"nom"	TEXT NOT NULL,
	"couleur"	TEXT DEFAULT '#FFFFFF',
	PRIMARY KEY("nom")
);
CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"type"	INTEGER NOT NULL DEFAULT 0,
	"nom"	TEXT NOT NULL,
	"prenom"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "questions" (
	"id"	INTEGER,
	"etiquette"	TEXT,
	"enonce"	TEXT NOT NULL,
	"user"	INTEGER NOT NULL,
	FOREIGN KEY("etiquette") REFERENCES "etiquettes"("nom") ON UPDATE RESTRICT ON DELETE RESTRICT,
	FOREIGN KEY("user") REFERENCES "users"("id") ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "reponses" (
	"id"	INTEGER,
	"question"	INTEGER,
	"reponse"	TEXT NOT NULL,
	FOREIGN KEY("question") REFERENCES "questions"("id") ON UPDATE CASCADE ON DELETE CASCADE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "etiquettes" VALUES ('algo','#000000');
INSERT INTO "users" VALUES (1,0,'doe','jhon','yolo18');
INSERT INTO "questions" VALUES (1,'algo','Comment tou tou pèle?',1);
INSERT INTO "reponses" VALUES (1,1,'Dounnouvahannne');
COMMIT;
