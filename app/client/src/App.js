import React, { Component } from "react";
import Grid from "@material-ui/core/Grid";
import OutlinedCard from "./components/OutlinedCard";
import ChartCard from "./components/ChartCard";
import Bar from "./components/Bar";
import FCMap from "./components/FCMap";
import StackedScrollableBar from "./components/StackedScrollableBar";

import GridItem from "./components/GridItem";
import ResponsiveDrawer from "./components/ResponsiveDrawer";
import KeplerMap from "./components/KeplerMap";
import { groupBy, map } from "lodash";
import moment from "moment";
import { Parser } from "json2csv";
import json2csv from "json2csv";

const containerStyle = {
  height: "100vh",
  width: "100vw",
  padding: "2em"
};

const dzongkhagToLabel = {
  Bumthang: "BT.BU",
  Chhukha: "BT.CK",
  Tsirang: "BT.CR",
  Dagana: "BT.DA",
  Gasa: "BT.GA",
  Sarpang: "BT.GE",
  Haa: "BT.HA",
  Lhuentse: "BT.LH",
  Monggar: "BT.MO",
  Paro: "BT.PR",
  Pema: "BT.PM",
  Punakha: "BT.PN",
  Samtse: "BT.SM",
  Samdrup: "BT.SJ",
  Zhemgang: "BT.SG",
  Trashigang: "BT.TA",
  Thimphu: "BT.TM",
  Trongsa: "BT.TO",
  Trashi: "BT.TY",
  Wangdue: "BT.WP"
};

class App extends Component {
  constructor() {
    super();
    this.state = {
      trips: [],
      tripsByDate: {},
      optimalRTRate: 50,
      summaryRow: [],
      chartsRow: [],
      avgRTByDzongkhag: [],
      numCallByDzongkhag: []
    };
  }

  componentDidMount() {
    this.loadDataFromServer();
  }

  loadDataFromServer = () => {
    fetch("/api/trips")
      .then(data => data.json())
      .then(res => {
        this.setState({ trips: res }, () => this.getData());
      });

    fetch("/api/facilities")
      .then(data => data.json())
      .then(res => {
        this.setState({ facilities: res });
      });
  };

  convertJsonToCsv = () => {
    const items = this.state.trips;
    const replacer = (key, value) => (value === null ? "" : value); // specify how you want to handle null values here
    const header = Object.keys(items[0]);
    let csv = items.map(row =>
      header
        .map(fieldName => JSON.stringify(row[fieldName], replacer))
        .join(",")
    );
    csv.unshift(header.join(","));
    csv = csv.join("\r\n");
    console.log(csv);
    this.setState({ csv });
  };

  calcAverageTime(data, start_time, end_time) {
    const MILISECONDS_IN_SECOND = 1000;
    const SECONDS_IN_MINUTE = 60;

    return Math.round(
      data.reduce((a, trip) => {
        return (
          a +
          Math.abs(new Date(trip[end_time]) - new Date(trip[start_time])) /
            (MILISECONDS_IN_SECOND * SECONDS_IN_MINUTE)
        );
      }, 0) / data.length,
      2
    );
  }

  calculateKPI(data, start_time, end_time, KPI) {
    const res =
      (data.reduce((a, trip) => {
        return (
          a +
          (Math.abs(new Date(trip[end_time]) - new Date(trip[start_time])) /
            (1000 * 60) <
            KPI)
        );
      }, 0) *
        100) /
      data.length;
    return res.toFixed(1);
  }

  buildSummaryCardConfig(data, start_time, end_time, title, label) {
    return {
      data: this.calcAverageTime(data, start_time, end_time),
      title: title,
      label: label
    };
  }

  getChartsRow() {
    const IDEAL_CALL_PROCESSING_TIME_MIN = 1;
    const IDEAL_TRAVEL_TIME_MIN = 8;
    const IDEAL_RESPONSE_TIME_MIN = 60;

    const optimalDispatchRate = this.calculateKPI(
      this.state.trips,
      "Dispatcher_Start",
      "OutgoingTrip_StartTime",
      IDEAL_CALL_PROCESSING_TIME_MIN
    );
    const optimalTravelTimeRate = this.calculateKPI(
      this.state.trips,
      "Dispatcher_Start",
      "OutgoingTrip_EndTime",
      IDEAL_TRAVEL_TIME_MIN
    );
    const optimalRTRate = this.calculateKPI(
      this.state.trips,
      "Dispatcher_Start",
      "ReturnTrip_EndTime",
      IDEAL_RESPONSE_TIME_MIN
    );

    return [
      {
        data: optimalDispatchRate,
        caption: `Dispatch within ${IDEAL_CALL_PROCESSING_TIME_MIN} min`,
        color: "#3B70C4, #000000"
      },
      {
        data: optimalTravelTimeRate,
        caption: `Travel time within ${IDEAL_TRAVEL_TIME_MIN} min`,
        color: "#41B6C4, #000000"
      },
      {
        data: optimalRTRate,
        caption: `Response time within ${IDEAL_RESPONSE_TIME_MIN} min`,
        color: "#EDF8B1, #000000"
      }
    ];
  }

  getData() {
    // this.convertJsonToCsv();

    const tripsByDate = groupBy(this.state.trips, function(trip) {
      return moment(new Date(trip["OutgoingTrip_StartTime"]))
        .startOf("day")
        .format();
    });

    var numTripsByDate = map(tripsByDate, function(group, day) {
      return {
        date: day,
        value: group.length
      };
    });

    const tripsByDzongkhag = groupBy(this.state.trips, function(trip) {
      return trip["Dispatcher_DzongkhagName"];
    });

    const avgRTByDzongkhag = Object.keys(tripsByDzongkhag).map(
      (dzongkhag, _) => {
        const avgResponseTime = this.calcAverageTime(
          tripsByDzongkhag[dzongkhag],
          "Dispatcher_Assigned",
          "OutgoingTrip_StartTime"
        );
        return {
          label: dzongkhag,
          value: avgResponseTime,
          displayValue: `${avgResponseTime} minutes`
        };
      }
    );

    const numCallByDzongkhag = Object.keys(tripsByDzongkhag).map(
      (dzongkhag, _) => {
        return {
          id: dzongkhagToLabel[dzongkhag.split(" ")[0]],
          value: tripsByDzongkhag[dzongkhag].length
        };
      }
    );

    const avgTurnoutTime = this.buildSummaryCardConfig(
      this.state.trips,
      "Dispatcher_Assigned",
      "OutgoingTrip_StartTime",
      "Average Turnout Time",
      "minutes"
    );
    const avgTravelTime = this.buildSummaryCardConfig(
      this.state.trips,
      "OutgoingTrip_StartTime",
      "OutgoingTrip_EndTime",
      "Average Travel Time",
      "minutes"
    );
    const avgTimeOnScene = this.buildSummaryCardConfig(
      this.state.trips,
      "OutgoingTrip_EndTime",
      "ReturnTrip_StartTime",
      "Average Time On Scene",
      "minutes"
    );
    const avgReturnTime = this.buildSummaryCardConfig(
      this.state.trips,
      "ReturnTrip_StartTime",
      "ReturnTrip_EndTime",
      "Average Return Time",
      "minutes"
    );
    const summaryRow = [
      avgTurnoutTime,
      avgTravelTime,
      avgTimeOnScene,
      avgReturnTime
    ];

    const chartsRow = this.getChartsRow();

    this.setState({
      tripsByDate,
      numTripsByDate,
      summaryRow,
      chartsRow,
      avgRTByDzongkhag,
      numCallByDzongkhag
    });
  }
  render() {
    return (
      <Grid container>
        <ResponsiveDrawer />
        {/* <SummaryNav /> */}
        <Grid container style={containerStyle}>
          {/* row 1 - summaries */}
          <Grid container direction="row">
            {this.state.summaryRow.map(row => (
              <GridItem key={row.title}>
                <OutlinedCard
                  title={row.title}
                  formatted_data={row.data}
                  label={row.label}
                />
              </GridItem>
            ))}
          </Grid>

          {/* row 2 - KPIs */}
          <Grid container direction="row">
            <GridItem xs={9}>
              <Grid container direction="row">
                {this.state.chartsRow.map(chart => (
                  <ChartCard
                    xs={3}
                    data={chart.data}
                    caption={chart.caption}
                    color={chart.color}
                    key={chart.caption}
                  />
                ))}
              </Grid>
            </GridItem>
          </Grid>

          {/* row 3 - chart*/}
          <Grid container direction="row">
            <GridItem xs={6}>
              <Bar
                data={this.state.avgRTByDzongkhag}
                caption="Average RT"
                subCaption="By Dzongkhag"
              />
              {/* <StackedScrollableBar 
                  data={this.state.avgRTByDzongkhag}
                  caption="Average RT"
                  subCaption="By Dzongkhag"
                /> */}
            </GridItem>

            <GridItem xs={6}>
              <FCMap
                data={this.state.numCallByDzongkhag}
                caption="Number of Calls"
                subCaption="By Dzongkhag"
              />
            </GridItem>
          </Grid>

          {/* row 4 - map*/}
          <Grid container justify="center" flexGrow={1}>
            <KeplerMap data={this.state.csv} />
          </Grid>
        </Grid>
      </Grid>
    );
  }
}

export default App;
