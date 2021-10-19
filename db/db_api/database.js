const sqlite3 = require("sqlite3").verbose();
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

const utils = require("./util.js");

let db = new sqlite3.Database(utils.ConfigManager.dbPath, (err) => {
  if (err) {
    console.log("Error connecting to SQlite database.");
    console.error(err.message);
    throw err;
  } else {
    console.log("Connected to the SQlite database.");
  }
});

module.exports = db;
