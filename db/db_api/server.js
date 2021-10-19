const express = require("express");
const app = express();
const db = require("./database.js");
const md5 = require("md5");
const bodyParser = require("body-parser");
const utils = require("./util.js");

app.use(bodyParser.urlencoded({
  extended: false
}));

app.use(bodyParser.json());

function accessControlOrigin(req, res, next) {
  console.log("access control allow origin handler middleware");
  res.header('Access-Control-Allow-Origin', "*");
  next();
}

function accessControlHeaders(req, res, next) {
  console.log("access control allow headers handler middleware");
  res.header('Access-Control-Allow-Headers', "*");
  next();
}

let accessControlMW = [accessControlOrigin, accessControlHeaders];
let httpPort = utils.ConfigManager.HTTPPort;

// Start server
app.listen(httpPort, () => {

  console.log(
    "Server running on port %PORT%".replace("%PORT%", httpPort)
  );

});

function sql_mng(req, res) {
  db.all(res.locals.sql_query, res.locals.sql_params, (err, row) => {

    if (err) {
      res.status(400).json({
        "error": err.message
      });
      return;
    }

    console.log("row", row);

    res.json({
      "message": "success",
      "data": row
    });

  });
}

app.get("/:asdu/:io/:limit", accessControlMW, (req, res, next) => {

  res.locals.sql_query =
    "SELECT * FROM t where asdu = ? and io = ? limit ?";

  res.locals.sql_params = [
    req.params.asdu,
    req.params.io,
    req.params.limit
  ];

  next();

}, sql_mng);

// Root path
app.get("/", (req, res, next) => {

  res.json({
    "message": "Ok",
    "elaborate": "server is running, make api call"
  });

});