psql postgres://programmed_differently_database_user:wKIRgoJYMCs9rIfDL6Hwx7nhDUzyuKbL@dpg-clitpn1b2fgs73b54190-a.frankfurt-postgres.render.com/programmed_differently_database

SELECT * FROM render_uploadmodel;

copy (SELECT * FROM render_uploadmodel) to 'C:tmpupload_db.csv' with csv
