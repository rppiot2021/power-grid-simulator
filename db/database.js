var sqlite3 = require('sqlite3').verbose()
var md5 = require('md5')

// database file name
const DBSOURCE = "../db_log/sql_db.db"

let db = new sqlite3.Database(DBSOURCE, (err) => {
    if (err) {
        console.log('Error connecting to SQlite database.');
        console.error(err.message);
        throw err;
    } else {
        console.log('Connected to the SQlite database.');
    }
})

module.exports = db;

