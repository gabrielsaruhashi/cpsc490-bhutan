import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";

const useStyles = makeStyles({
  card: {
    backgroundColor: "#202a3b!important",
    padding: "1.5em"
  },
  title: {
    fontSize: 14,
    color: "#8091ab",
    fontWeight: 400
  },
  pos: {
    marginBottom: 12
  },
  data: {
    fontWeight: "bold",
    color: "white"
  }
});

const OutlinedCard = props => {
  const classes = useStyles();
  const bull = <span className={classes.bullet}>•</span>;
  const { title, icon, formatted_data, label } = props;
  return (
    <Card className={classes.card} variant="outlined">
      <CardContent>
        <Typography
          className={classes.title}
          color="textSecondary"
          gutterBottom
        >
          {title}
        </Typography>
        <Typography variant="h5" component="h2" className={classes.data}>
          {formatted_data}
          {label}
        </Typography>
      </CardContent>
      {/* <CardActions>
        <Button size="small">Learn More</Button>
      </CardActions> */}
    </Card>
  );
};

export default OutlinedCard;
