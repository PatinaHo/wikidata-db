\copy title_table (wdid,entitle,zhhanttitle,zhhanstitle) FROM './table-id-title.csv' DELIMITER ',' CSV HEADER;

\copy relation_table (sourceid,targetid,relation) FROM './table-relation.csv' DELIMITER ',' CSV HEADER;