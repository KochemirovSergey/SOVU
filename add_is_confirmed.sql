-- Добавление поля is_confirmed в таблицу graduate_school
ALTER TABLE graduate_school ADD COLUMN is_confirmed BOOLEAN NOT NULL DEFAULT 0;

-- Добавление поля is_confirmed в таблицу teacher_school
ALTER TABLE teacher_school ADD COLUMN is_confirmed BOOLEAN NOT NULL DEFAULT 0;