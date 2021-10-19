let sqlite3 = require("sqlite3").verbose();
const fs = require('fs');
const yaml = require('js-yaml');
const path = require('path');

//module.exports = function getFromConfig() {
//    console.log("ff");
//
//}
//
//exports.getFromConfig = function() {
//  console.log("aaa")
//
//}

class ConfigManager {

  constructor(configFilePath = "../conf.yaml") {
    console.log("file path", configFilePath)

    let fileContents = fs.readFileSync(configFilePath, 'utf8');
    let data = yaml.loadAll(fileContents);
    let dbConfig = data[0]["database_manager"];

    this.dbConfig = dbConfig;
  }

  get dbPath() {

    let fullPath = this.dbConfig["prefix"] === "None" ?
      "" : this.dbConfig["prefix"];

    fullPath += path.join(
      this.dbConfig["default_database_folder"],
      this.dbConfig["default_database_filename"]
    );

    return fullPath;

  }

  get HTTPPort() {
      return this.dbConfig["port"];
  }

}

exports.ConfigManager = new ConfigManager();
