var express = require("express")
var app = express()
var db = require("./database.js")
var md5 = require("md5")
var bodyParser = require("body-parser");

var utils = require("./util.js")

utils.getFromConfig()
utils.ConfigManager.foo();

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

var accessControlMW = [accessControlOrigin, accessControlHeaders]

var httpport = utils.ConfigManager.HTTPPort;

// Start server
app.listen(httpport, () => {
    console.log("Server running on port %PORT%".replace("%PORT%", httpport))
});

let sql_query;
let sql_params;

function sql_mng(req, res) {
    db.all(sql_query, sql_params, (err, row) => {
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

    sql_query = "SELECT * FROM t where asdu = ? and io = ? limit ?";

    sql_params = [req.params.asdu, req.params.io, req.params.limit];
    next();

}, sql_mng);

// Root path
app.get("/", (req, res, next) => {
    res.json({
        "message": "Ok",
        "elaborate": "server is running, make api call"
    });
});