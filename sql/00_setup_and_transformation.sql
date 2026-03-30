-- =============================================================================
-- PROYECTO: Sistema de Inteligencia de Riesgo Crediticio - Colombia 2026
-- AUTOR: Santiago Cruz (Cruz227)
-- DESCRIPCIÓN: Creación de esquema, enriquecimiento de datos (Ciberseguridad, 
--              Geografía, Estacionalidad) y ETL para conversión de moneda.
-- =============================================================================

-- 1. CREACIÓN DE LA ESTRUCTURA DE LA TABLA (Ingesta de datos crudos)
-- El dataset original proviene de Kaggle (Credit Risk Dataset)
CREATE TABLE prestamos (
    person_age INT,
    person_income INT,
    person_home_ownership VARCHAR(50),
    person_emp_length FLOAT,
    loan_intent VARCHAR(100),
    loan_grade VARCHAR(5),
    loan_amnt INT,
    loan_int_rate FLOAT,
    loan_status INT, -- 0: Al día, 1: Moroso
    loan_percent_income FLOAT,
    cb_person_default_on_file VARCHAR(5),
    cb_person_cred_hist_length INT
);

-- 2. ENRIQUECIMIENTO DE DATOS (Capa de Ingeniería de Datos)
-- Agregamos columnas para Ciberseguridad, Localización y Estacionalidad
ALTER TABLE prestamos 
ADD COLUMN cliente_hash TEXT,
ADD COLUMN departamento_colombia VARCHAR(50),
ADD COLUMN fecha_desembolso DATE;

-- 2.1. Ciberseguridad: Anonimización de IDs mediante Hashing MD5 (Habeas Data)
UPDATE prestamos SET cliente_hash = MD5(CAST(RANDOM() AS TEXT));

-- 2.2. Localización: Asignación de Departamentos de Colombia
UPDATE prestamos 
SET departamento_colombia = (ARRAY['Antioquia', 'Bogotá', 'Valle', 'Atlántico', 'Santander', 'Bolívar'])[FLOOR(RANDOM() * 6 + 1)];

-- 2.3. Estacionalidad: Generación de fechas de desembolso (Ciclo 2024-2025)
UPDATE prestamos 
SET fecha_desembolso = '2024-01-01'::date + (random() * 730)::integer;

-- 3. CREACIÓN DE LA VISTA DE CONSUMO (Capa de ETL y Negocio)
-- Esta vista es la fuente oficial para Power BI y el Agente de IA en Python.
-- Realiza la conversión de USD a COP (TRM 4,000) y previene errores de desbordamiento (BigInt).

DROP VIEW IF EXISTS v_prestamos_limpios;

CREATE VIEW v_prestamos_limpios AS
SELECT 
    cliente_hash AS id_cliente_anonimizado, -- Identificador seguro
    departamento_colombia AS departamento,  -- Geointeligencia
    fecha_desembolso,                       -- Análisis temporal
    person_age AS edad,
    -- Transformación monetaria a COP usando BIGINT para evitar 'NumericValueOutOfRange'
    CAST(person_income AS BIGINT) * 4000 AS ingresos_anuales_cop, 
    CAST(loan_amnt AS BIGINT) * 4000 AS monto_prestamo_cop,
    -- Traducción de categorías para Dashboards en español
    CASE 
        WHEN person_home_ownership = 'RENT' THEN 'Renta'
        WHEN person_home_ownership = 'MORTGAGE' THEN 'Hipoteca'
        WHEN person_home_ownership = 'OWN' THEN 'Propio'
        ELSE 'Otro'
    END AS tipo_vivienda,
    person_emp_length AS años_experiencia,
    CASE 
        WHEN loan_intent = 'PERSONAL' THEN 'Personal'
        WHEN loan_intent = 'EDUCATION' THEN 'Educación'
        WHEN loan_intent = 'MEDICAL' THEN 'Salud'
        WHEN loan_intent = 'VENTURE' THEN 'Emprendimiento'
        WHEN loan_intent = 'HOMEIMPROVEMENT' THEN 'Mejoras Hogar'
        WHEN loan_intent = 'DEBTCONSOLIDATION' THEN 'Consolidación Deuda'
    END AS motivo_prestamo,
    loan_grade AS categoria_riesgo,
    loan_int_rate AS tasa_interes,
    CASE 
        WHEN loan_status = 1 THEN 'Moroso'
        ELSE 'Al día'
    END AS estado_pago,
    loan_percent_income AS porcentaje_ingreso_prestamo,
    cb_person_cred_hist_length AS años_historial_crediticio
FROM prestamos
WHERE person_age <= 90              -- Limpieza de Outliers de edad
  AND person_emp_length <= 60      -- Limpieza de Outliers laborales
  AND loan_int_rate IS NOT NULL;   -- Aseguramiento de integridad de tasa