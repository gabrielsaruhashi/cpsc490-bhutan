const express = require("express");
const bodyParser = require("body-parser");
const path = require("path");

var db = require("./database");
var schedule = require("node-schedule");

const ENV = process.env.NODE_ENV;
const PORT = process.env.PORT || 8080;

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(bodyParser.json({ limit: "50mb", extended: true }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: true }));

app.use("/api/trips", require("./api/trips"));
app.use("/api/facilities", require("./api/facilities"));

if (ENV === "production") {
  app.use(express.static(path.join(__dirname, "../client/build")));
  app.use((req, res) => {
    res.sendFile(path.join(__dirname, "../client/build/index.html"));
  });
}

db.query("SELECT NOW()", (err, res) => {
  if (err.error) return console.log(err.error);
  console.log(`PostgreSQL connected: ${res[0].now}.`);
});
process.on("SIGINT", () => {
  console.log("Bye bye!");
  process.exit();
});

var job = schedule.scheduleJob("0 0 * * *", () => {
  console.log("hey");
});

app.get("/scrape", callScrape);

function callScrape(req, res) {
  var spawn = require("child_process").spawn;

  var process = spawn("python", [
    "../../scraping/server_scrape.py",
    "../../scraping/chromedriver",
    req.query.start_date,
    req.query.end_date
  ]);

  // Takes stdout data from script which executed
  // with arguments and send this data to res object
  process.stdout.on("data", function(data) {
    res.send(data.toString());
  });

  process.stderr.on("data", data => {
    console.error(`stderr: ${data}`);
  });

  process.on("close", code => {
    console.log(`child process exited with code ${code}`);
  });
}

// Use our router configuration when we call /api
// app.use("/api", router);
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}!`);
});

module.exports = app;
