let sqlite3 = require("sqlite3").verbose();
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

function getDbPath() {
  let fileContents = fs.readFileSync('../conf.yaml', 'utf8');
  let data = yaml.loadAll(fileContents);
  let dbConfig = data[0]["database_manager"];

  let fullPath = dbConfig["prefix"] === "None" ? "" : dbConfig["prefix"];

  fullPath += path.join(
    dbConfig["default_database_folder"],
    dbConfig["default_database_filename"]
  );

  console.log(fullPath);

  return fullPath;
}

let db = new sqlite3.Database(getDbPath(), (err) => {
  if (err) {
    console.log("Error connecting to SQlite database.");
    console.error(err.message);
    throw err;
  } else {
    console.log("Connected to the SQlite database.");
  }
});

module.exports = db;
