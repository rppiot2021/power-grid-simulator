let sqlite3 = require("sqlite3").verbose();

// database file name
const DB_SOURCE = "../db_log/sql_db.db_api";

const fs = require('fs');
const yaml = require('js-yaml');

try {
    // let fileContents = fs.readFileSync('./data-multi.yaml', 'utf8');
    let fileContents = fs.readFileSync('../conf.yaml', 'utf8');

    let data = yaml.loadAll(fileContents);

    let db_config = data[0]["database_manager"]

    console.log(db_config)
    // console.log(data[0]["database_manager"])

    console.log("data------------------------------------")
    console.log(data);
} catch (e) {
    console.log(e);
}
//
// let db = new sqlite3.Database(DB_SOURCE, (err) => {
//   if (err) {
//     console.log("Error connecting to SQlite database.");
//     console.error(err.message);
//     throw err;
//   } else {
//     console.log("Connected to the SQlite database.");
//   }
// });
//
// module.exports = db;
