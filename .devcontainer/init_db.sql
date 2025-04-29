-- Limpiar
DROP TABLE IF EXISTS casillapixel;
DROP TABLE IF EXISTS boleto;
DROP TABLE IF EXISTS imagen;
DROP TABLE IF EXISTS pregunta;
DROP TABLE IF EXISTS evento;
DROP TABLE IF EXISTS usuario;

-- Tablas
CREATE TABLE usuario (
  idusuario INT IDENTITY(1,1) PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  contrasena CHAR(40) NOT NULL,
  puntaje INT
);

CREATE TABLE boleto (
  idboleto INT IDENTITY(1,1) PRIMARY KEY,
  tipo INT,
  idusuario_usuario INT NOT NULL,
  FOREIGN KEY (idusuario_usuario) REFERENCES usuario (idusuario)
);

CREATE TABLE evento (
  idevento INT IDENTITY(1,1) PRIMARY KEY,
  horainicio DATETIME,
  horafin DATETIME
);

CREATE TABLE imagen (
  idimagen INT IDENTITY(1,1) PRIMARY KEY,
  respuesta INT,
  horarespuesta DATETIME,
  idevento_evento INT,
  FOREIGN KEY (idevento_evento) REFERENCES evento (idevento)
);

CREATE TABLE pregunta (
  idpregunta INT IDENTITY(1,1) PRIMARY KEY,
  opcionA VARCHAR(50),
  opcionB VARCHAR(50),
  opcionC VARCHAR(50),
  opcionD VARCHAR(50),
  opcioncorrecta INT,
  numVecesRespondida INT,
  pregunta VARCHAR(255)
);

CREATE TABLE casillapixel (
  idpixel INT IDENTITY(1,1) PRIMARY KEY,
  estado VARCHAR(10) NOT NULL DEFAULT 'inactivo',
  posicion INT NOT NULL,
  idimagen_imagen INT,
  idusuario_usuario INT NOT NULL,
  idpregunta_pregunta INT,
  FOREIGN KEY (idimagen_imagen) REFERENCES imagen (idimagen),
  FOREIGN KEY (idusuario_usuario) REFERENCES usuario (idusuario),
  FOREIGN KEY (idpregunta_pregunta) REFERENCES pregunta (idpregunta)
);

-- Datos
INSERT INTO usuario (username, contrasena, puntaje) VALUES
('user1', '1234567890123456789012345678901234567890', 100),
('user2', 'abcdefabcdefabcdefabcdefabcdefabcdefabcd', 200),
('user3', 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeef', 150);

INSERT INTO boleto (tipo, idusuario_usuario) VALUES
(1, 1),
(2, 2),
(1, 3);

INSERT INTO evento (horainicio, horafin) VALUES
('2025-03-26 10:00:00', '2025-03-26 11:00:00'),
('2025-03-27 14:00:00', '2025-03-27 15:00:00');

INSERT INTO imagen (respuesta, horarespuesta, idevento_evento) VALUES
(2, '2025-03-26 10:45:00', 1),
(4, '2025-03-27 14:30:00', 2);

INSERT INTO pregunta (opcionA, opcionB, opcionC, opcionD, opcioncorrecta, numVecesRespondida, pregunta) VALUES
('Rojo', 'Azul', 'Verde', 'Amarillo', 2, 10, '¿Cuál es el color del cielo?'),
('5', '6', '7', '8', 3, 5, '¿Cuánto es 3 + 4?');

INSERT INTO casillapixel (estado, posicion, idimagen_imagen, idusuario_usuario, idpregunta_pregunta) VALUES
('activo', 1, 1, 1, 1),
('inactivo', 2, 1, 2, 2),
('activo', 3, 2, 3, 1);
