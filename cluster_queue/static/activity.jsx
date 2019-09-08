const Plot = createPlotlyComponent(Plotly);

class PercentagePlot extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      yValue: Array(props.nBars)
        .fill(0),
      currAnimationIncrementList: 0,
      animationIncrements: props.animationIncrements,
      xValue: [...Array(props.nBars)
        .keys()
      ],
      dataUrl: props.dataUrl
    };
  }

  updatePlotAnimation() {
    const yValue = this.state.yValue.map((val, index) => {
      return val + this.state.currAnimationIncrementList[index];
    });
    this.setState({
      yValue: yValue
    });
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl)
      .then(res => res.json())
      .then(
        (result) => {

          const plotSteps = this.state.yValue.map((val, index) => {
            return (result['cpu_usage'][index] - val) / this.state
              .animationIncrements;
          });

          this.setState({
            'currAnimationIncrementList': plotSteps,
          });

          for (var x = 0; x <= this.state.animationIncrements; x++) {
            setTimeout(this.updatePlotAnimation.bind(this), x * this.state
              .updateInterval);
          }
        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
  }

  fetchActivityPeriodic() {
    this.fetchActivity();
    setTimeout(this.fetchActivityPeriodic.bind(this), 1000);
  }

  componentDidMount() {
    this.fetchActivityPeriodic();
  }

  render() {
    return (
      <div className="container">
        <Plot data={[{
                type: 'bar',
                x: this.state.xValue,
            y: this.state.yValue,
            }]}
              layout={{
                  xaxis: {
                      title : '',
                      showticklabels : false,
                  },
                  yaxis: {
                      range : [0, 100]
                  },
                  width: '100%',
                  height: '100%',
                  title: 'CPU Usage'}}
        />
      </div>
    );
  }
}

ReactDOM.render(
  <PercentagePlot
      dataUrl={"/cluster/activity"}
      nBars={12}
      animationIncrements={10}
    />,
  document.getElementById('root')
);
