const db = require("../database");

class Facility {
  static retrieveAll(callback) {
    db.query("SELECT * from facilities", (err, res) => {
      if (err.error) return callback(err);
      callback(res);
    });
  }
}

module.exports = Facility;
