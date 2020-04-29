const db = require("../database");

class Trip {
  static retrieveAll(callback) {
    db.query("SELECT * from er_trips", (err, res) => {
      if (err.error) return callback(err);
      callback(res);
    });
  }

//   static insert(desc, callback) {
//     db.query(
//       "INSERT INTO er_trips (description) VALUES ($1)",
//       [desc],
//       (err, res) => {
//         if (err.error) return callback(err);
//         callback(res);
//       }
//     );
//   }
}

module.exports = Trip;