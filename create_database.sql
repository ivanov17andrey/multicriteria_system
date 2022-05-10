CREATE TABLE IF NOT EXISTS links
(
    Id   serial primary key,
    link text
);

ALTER TABLE links
    ADD COLUMN processed boolean DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS helicopters
(
    id       serial primary key,
    name     text,
    weight   smallint,
    duration smallint,
    distance smallint,
    height   smallint,
    speed    smallint,
    pixels   smallint,
    fps      smallint,
    rating   decimal,
    price    integer
);

ALTER TABLE helicopters
    ADD COLUMN link_id integer REFERENCES links (id);

CREATE TABLE IF NOT EXISTS criteria
(
    id   serial primary key,
    num  smallint,
    name varchar(255)
)
;


ALTER TABLE criteria
    ADD COLUMN coefficient smallint default 1;

ALTER TABLE criteria
    ADD COLUMN direction varchar(255) default 'max';