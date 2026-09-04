CREATE DATABASE IF NOT EXISTS juego_app;
USE juego_app;

#tabla
CREATE TABLE jugadores (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nickname    VARCHAR(50) NOT NULL UNIQUE,
    victorias   INT DEFAULT 0,
    derrotas    INT DEFAULT 0
);

#TABLA DE PARTIDAS
#Guarda cada resultado con fecha y hora
CREATE TABLE partidas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nickname_ganador VARCHAR(50) NOT NULL,
    nickname_perdedor VARCHAR(50) NOT NULL,
    fecha_hora      DATETIME DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$
CREATE PROCEDURE registrar_resultado(
    IN p_ganador   VARCHAR(50),
    IN p_perdedor  VARCHAR(50)
)
BEGIN
    -- Insertamos ganador si no existe, sumar victoria si ya existe
    INSERT INTO jugadores (nickname, victorias, derrotas)
        VALUES (p_ganador, 1, 0)
        ON DUPLICATE KEY UPDATE victorias = victorias + 1;

    -- Insertamos perdedor si no existe, sumar derrota si ya existe
    INSERT INTO jugadores (nickname, victorias, derrotas)
        VALUES (p_perdedor, 0, 1)
        ON DUPLICATE KEY UPDATE derrotas = derrotas + 1;

    -- Registrar la partida
    INSERT INTO partidas (nickname_ganador, nickname_perdedor)
        VALUES (p_ganador, p_perdedor);
END$$

DELIMITER ;

#consulta
SELECT 
    nickname,
    victorias,
    derrotas,
    (victorias + derrotas) AS partidas_jugadas
FROM jugadores
ORDER BY victorias DESC;

-- =============================================
-- PRUEBA: simular una partida
-- =============================================
CALL registrar_resultado('PlayerPC', 'PlayerAndroid');
CALL registrar_resultado('PlayerPC', 'PlayerAndroid');
CALL registrar_resultado('PlayerAndroid', 'PlayerPC');

-- Ver resultado
SELECT * FROM jugadores;
SELECT * FROM partidas;

UPDATE jugadores SET nickname = TRIM(nickname);
UPDATE partidas SET nickname_ganador = TRIM(nickname_ganador);
UPDATE partidas SET nickname_perdedor = TRIM(nickname_perdedor);

-- Limpiar datos de prueba
SET SQL_SAFE_UPDATES = 0;
DELETE FROM partidas;
DELETE FROM jugadores;
ALTER TABLE jugadores AUTO_INCREMENT = 1;
ALTER TABLE partidas AUTO_INCREMENT = 1;