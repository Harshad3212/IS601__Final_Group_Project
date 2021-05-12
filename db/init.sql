CREATE DATABASE covidData;
use covidData;

CREATE TABLE IF NOT EXISTS tblCount (
    `Month` VARCHAR(5),
    `count` INT
);
INSERT INTO tblCount VALUES
    ('Jun', 24109),
    ('July',18956),
    ('Aug',20743),
    ('Sep',24783),
    ('Oct',33349),
    ('Nov',153206),
    ('Dec',328657);

CREATE TABLE IF NOT EXISTS users(id INT(11) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), username VARCHAR(30), password VARCHAR(100));




