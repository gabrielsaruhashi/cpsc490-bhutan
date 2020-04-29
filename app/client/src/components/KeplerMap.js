import KeplerGl from "kepler.gl";
import React, { Component } from "react";
import { processCsvData } from "kepler.gl/processors";
import { addDataToMap, addNotification } from "kepler.gl/actions";
import { connect } from "react-redux";
import {
  tripDataConfig,
  tripData,
  facilityData,
  facilityDataConfig
} from "./sample-trip-data";
import AutoSizer from "react-virtualized/dist/commonjs/AutoSizer";
import "react-virtualized/styles.css";

class KeplerMap extends Component {
  componentDidMount() {
    this.loadData();
  }
  componentDidUpdate() {
    console.log(this.props.keplerGl.map.mapState);
    console.log(this.props.keplerGl);
    // console.log(this.props.getBounds)
  }

  loadData() {
    this.props.dispatch(
      addDataToMap({
        datasets: [
          {
            info: {
              label: "Emergency Response in Bhutan",
              id: "trip_data"
            },
            data: processCsvData(tripData)
          },
          {
            info: {
              label: "Emergency Response in Bhutan",
              id: "facility_data"
            },
            data: processCsvData(facilityData)
          }
        ],
        options: {
          centerMap: true,
          readOnly: false
        },
        config: tripDataConfig
      })
    );
  }

  render() {
    return (
      // <AutoSizer>
      //   {({height, width}) => (
      // <div
      //     style={{
      //       transition: 'margin 1s, height 1s',
      //       position: 'center',
      //       flexGrow: 1,
      //       // height: showBanner ? `calc(100% - ${BannerHeight}px)` : '100%',
      //       // minHeight: `calc(100% - ${BannerHeight}px)`,
      //       // marginTop: showBanner ? `${BannerHeight}px` : 0
      //     }}
      //   >

      <KeplerGl
        height={500}
        width={750}
        id="map"
        mapboxApiAccessToken={
          "pk.eyJ1IjoiZ2FicmllbHNhcnVoYXNoaSIsImEiOiJjazRvYnJrcmQzYnlpM29uYXQxMXg4ZjN1In0.mlHyCTMMuM8SFwNoIr9DqA"
        }
      />
      // </div>
      // )}
      // </AutoSizer>
    );
  }
}

const mapStateToProps = state => state;
const dispatchToProps = dispatch => ({ dispatch });

export default connect(mapStateToProps, dispatchToProps)(KeplerMap);
