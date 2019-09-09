const Plot = createPlotlyComponent(Plotly);

class Layout extends React.Component {
  constructor(props) {
    super(props);

    const cores = 12;

    this.state = {
      nCores: cores,
      cpuActivity: Array(cores)
        .fill(0),
      cpuActivityHistory: Array(cores)
        .fill(0)
        .map((v) => {
          return [v];
        }),
      dataUrl: props.dataUrl,
      serverUpdateInterval: 5000,
    };

    setInterval(this.fetchActivity.bind(this), this.state
      .serverUpdateInterval);
  }

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl)
      .then(res => res.json())
      .then(
        (result) => {
          const cpuHistory =
            this.state.cpuActivityHistory.map((series, index) => {
              const new_val = result['cpu_usage'][index];
              return series.concat(new_val);
            });

          this.setState({
            cpuActivity: result['cpu_usage'],
            cpuActivityHistory: cpuHistory
          });
        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
  }

  render() {
    return (
      <div>
        <AnimatedBarPlot
              nBars={this.state.nCores}
              animationIncrements={10}
              targetYValue={this.state.cpuActivity}
              maxYValue={100} />
        <TimeLinePlot yValues={this.state.cpuActivityHistory}/>
      </div>
    );
  }
}

class TimeLinePlot extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      yValues: this.props.yValues,
      maxYValue: 100
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.yValues !== prevProps.yValues) {
      this.setState({
        yValues: this.props.yValues
      });
    }
  }

  render() {
    const data = this.state.yValues.map((series, index) => {
      return {
        mode: 'lines',
        line: {
        },
        y: series,
      };
    });

    return (
      <div className="container">
        <Plot data={data}
                    layout={{
                        xaxis: {
                            title : 'Time',
                            showticklabels : false,
                        },
                        yaxis: {
                            range : [0, this.state.maxYValue]
                        },
                        width: '100%',
                        height: '100%',
                        title: 'CPU Vs Time'}}
              />
            </div>
    );
  }
}

class AnimatedBarPlot extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      yValue: Array(props.nBars)
        .fill(0),
      targetYValue: props.targetYValue,
      easingStepSize: 5,
      maxYValue: props.maxYValue,
      easingUpdateInterval: 100,
      xValue: [...Array(props.nBars)
        .keys()
      ],
    };

    setInterval(this.updatePlotAnimation.bind(this), this.state
      .easingUpdateInterval);
  }

  updatePlotAnimation() {
    /* Moves yValue closer to yValueTarget by up to easingStepSize. This is to make transitions smoother (by limiting the movement permitted for each "frame"). Note that this implementation does mean bars don't finish moving at the same time, but it is simpler to implement with an external data source */
    const yValue = this.state.yValue.map((val, index) => {
      const diff = this.state.targetYValue[index] - val;
      const step = Math.sign(diff) * Math.min(this.state.easingStepSize,
        Math.abs(diff));
      return val + step;
    });
    this.setState({
      yValue: yValue
    });
  }

  componentDidUpdate(prevProps) {
    if (this.props.targetYValue !== prevProps.targetYValue) {
      this.setState({
        targetYValue: this.props.targetYValue
      });
    }
  }

  render() {
    return (
      <div className="container">
        <Plot data={[{
                type: 'bar',
                x: this.state.xValue,
            y: this.state.yValue,
            marker : {
                color : this.state.yValue.map((y) => y/this.state.maxYValue ),
                /* note: default colorscales in src/components/colorscale/scales.js */
                colorscale: [[0, 'rgb(50,168,82)'],
                             [0.75, 'rgb(50,168,82)'],
                             [1, 'rgb(255,0,30)']]
            }
            }]}
              layout={{
                  xaxis: {
                      title : '',
                      showticklabels : false,
                  },
                  yaxis: {
                      range : [0, this.state.maxYValue]
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
  <Layout dataUrl={"/cluster/activity"} />,
  document.getElementById('root')
);
