const Plot = createPlotlyComponent(Plotly);

class DynamicUpdateBarPlot extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      yValue: Array(props.nBars)
        .fill(0),
      targetYValue: Array(props.nBars)
        .fill(0),
      easingStepSize: 5,
        maxYValue: 100, 
      easingUpdateInterval: 100,
      xValue: [...Array(props.nBars)
        .keys()
      ],
      dataUrl: props.dataUrl
    };


    setInterval(this.fetchActivity.bind(this), 5000);
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

  // fetch best simulations from server and update in component state
  fetchActivity() {
    fetch(this.state.dataUrl)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            'targetYValue': result['cpu_usage'],
          });

        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
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
  <DynamicUpdateBarPlot
      dataUrl={"/cluster/activity"}
      nBars={12}
      animationIncrements={10}
    />,
  document.getElementById('root')
);
