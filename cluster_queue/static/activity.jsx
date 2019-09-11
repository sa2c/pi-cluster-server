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
      maxNumHistoryEntries: 20,
      dataUrl: props.dataUrl,
      serverUpdateInterval: 5000,
      pending: [],
      running: [],
      coreMappings: [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [8, 9, 10, 11],
        [12, 13, 14, 15]
      ],
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
              const next_val = result['cpu_usage'][index];
              const nmax = this.state.maxNumHistoryEntries;
              return series.concat(next_val)
                .slice(series.length - nmax + 1, series.length + 1);
            });

          this.setState({
            cpuActivity: result['cpu_usage'],
            cpuActivityHistory: cpuHistory,
            pending: result['pending'],
            running: result['running'],

          });
        },
        (error) => {
          console.log("failed to load data from " + this.state.dataUrl);
        }
      );
  }

  render() {
    const cpuActivity = this.state.coreMappings.map((rows) => {
      return rows.map((core_id) => {
        return this.state.cpuActivity[core_id];
      });
    });

    return (
      <div id="layout">
        <div className="lhs-pane">
          <ClusterSchematic values={cpuActivity} />
        </div>
        <div className="rhs-pane">
          <TimeLinePlot yValues={this.state.cpuActivityHistory}/>
          <h1 className="title is-2">Waiting</h1>
          <SimulationList simulations={this.state.pending}/>
          <h1 className="title is-2">Running</h1>
          <SimulationList simulations={this.state.running}/>
        </div>
      </div>
    );
  }
}

class SimulationList extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      simulations: this.props.simulations,
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.simulations !== prevProps.simulations) {
      this.setState({
        simulations: this.props.simulations,
      });
    }
  }

  render() {
    return this.state.simulations.map((sim) => {
      return <SimulationView key={sim['id']} simulation={sim}/>;
    });
  }
}

class SimulationView extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      simulation: this.props.simulation,
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.simulation !== prevProps.simulation) {
      this.setState({
        simulation: this.props.simulation,
      });
    }
  }

  render() {

    const simulation = this.state.simulation;

    if (simulation == undefined) {
      return <div className="simulation-data"/>;
    } else {
      const sim_id = simulation['id'];

      const image_url = "simulations/" + sim_id +
        "/elmeroutput0001-velomagn.png";

      const image_alt = "Simulation " + sim_id + " image";

      return (
        <div className="simulation-data" style={{width: "30%", float : "left" }}>
            <p>
              {simulation['name']}
            </p>
              <img src={image_url}
                   alt={image_alt}
                   width="100%" />

            </div>
      );
    }
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
        line: {},
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
                            range : [0, this.state.maxNumHistoryEntries]
                        },
                        yaxis: {
                            title : 'Percentage',
                            range : [0, this.state.maxYValue]
                        },
                        showlegend: false,
                        width: '850px',
                        height: '200px',
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
                      title : 'Percentage',
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

class PercentageGauge extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      value: props.value,
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.value !== prevProps.value) {
      this.setState({
        value: this.props.value,
      });
    }
  }
  render() {
    return (
      <div className="progress-gauge">
        <span className="text">
          {Math.round(this.state.value) + "%"}
        </span>
        <div className = "mask" style = {{ width: (100 - this.state.value) + "%" }} />
      </div>
    );
  }
}

class ClusterCore extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      value: props.value,
    };
  }

  componentDidUpdate(prevProps) {
    if (this.props.value !== prevProps.value) {
      this.setState({
        value: this.props.value,
      });
    }
  }

  render() {
    return (
      <div className="cluster-core">
        <PercentageGauge value={this.state.value}/>
      </div>
    );
  }
}

class ClusterNetworkCanvas extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      cableStyles: {
        "blue": [
          [0, 0],
          [0, 1],
          [1, 0],
          [1, 1],
        ],
        "orange": [
          [0, 2],
          [0, 3],
          [1, 2],
          [1, 3],
        ],
        "#DDDDDD": [
          [2, 0],
          [2, 1],
          [2, 2],
          [2, 3],
          [3, 0],
          [3, 1],
          [3, 2],
          [3, 3],
        ]
      },
      packetStyles: {
        "white": [
          [0, 0],
          [0, 1],
          [0, 2],
          [0, 3],
          [1, 0],
          [1, 1],
          [1, 2],
          [1, 3],
        ]
      }
    };
  }

  componentDidMount() {
    const canvas = document.getElementById('cluster-schematic-canvas');
    const ctx = canvas.getContext('2d');

    this.setState({
      ctx: ctx
    }, () => {
      setInterval(this.drawNetworkLines.bind(this), 500);
    });
  }

  drawNetworkLines() {
    const gapLen = 275;
    var dashOffset =
      (Math.round((new Date()
        .getTime() / 1000) * 10)) % gapLen;

    this.doDrawNetworkLines(this.state.cableStyles, [0, 0], 4, 0);
    this.doDrawNetworkLines(this.state.packetStyles, [5, 50, 5, 25, 5, 200],
      3, dashOffset);
  }

  doDrawNetworkLines(styles, dashes, width, start_offset) {
    var ctx = this.state.ctx;

    ctx.lineWidth = width;
    ctx.setLineDash(dashes);

    Object.keys(styles)
      .map((key) => {
        ctx.beginPath();
        ctx.strokeStyle = key;

        styles[key].map((val) => {
          const row = val[0];
          const col = val[1];

          this.drawSingleNetworkLine(row, col, start_offset, ctx);
        });

        ctx.stroke();

      });

  }

  drawCorner(ctx, x, y, r, quartile) {
    const startAngle = (quartile - 1) / 2;

    ctx.arc(x, y, r, startAngle * Math.PI, (startAngle + 0.5) * Math
      .PI);
  }

  drawSingleNetworkLine(row, col, start_offset, ctx) {

    const xNetwork = 94.5 + 145 * col;
    const yNetwork = 19.5 + (165 * row);
    const xWidth = 60 - 10 * row;
    const yBottom = 655;
    const yBottomOffset = [30, 20, 10, 0];
    const xNetworkOffset = [0, -50, -80, -100];
    const heightFirstSegment = 12;
    const r = 5;

    ctx.moveTo(xNetwork, yNetwork + start_offset);
    ctx.arc(xNetwork + r, yNetwork - heightFirstSegment, r, Math.PI, 1.5 *
      Math.PI);
    ctx.arc(xNetwork + xWidth - r, yNetwork - heightFirstSegment, r, 1.5 *
      Math.PI, 2 * Math.PI);
    if (xNetworkOffset[row] != 0) {
      ctx.arc(xNetwork + xWidth - r, yBottom + yBottomOffset[row] - r, r, 0,
        0.5 * Math.PI);
      ctx.arc(xNetwork + xWidth + xNetworkOffset[row] + r,
        yBottom + yBottomOffset[row] + r,
        r, 1.5 * Math.PI, Math.PI, true);
    }
    ctx.lineTo(xNetwork + xWidth + xNetworkOffset[row], yBottom + 35);
  }

  render() {
    return (
      <canvas id="cluster-schematic-canvas" width="600px" height="728px"/>
    );
  }

}

class ClusterSchematic extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      values: [
        /* list of columns */
        [10, 30, 10, 50],
        [11, 31, 11, 51],
        [10, 30, 10, 50],
        [10, 30, 10, 50],
      ],
      maxYValue: props.maxYValue,
    };
    if (this.props.debug) {
      setInterval(this.applyRandomUpdates.bind(this), 1000);
    }
  }

  applyRandomUpdates() {
    /* for testing purposes, this applies random changes to the initial values */
    var movement = 20;
    var new_state = this.state.values.map((val) => {
      return val.map((val) => {
        val = val + (Math.random() - 0.5) * 2 * movement;
        return Math.min(Math.max(val, 0), 98);
      });
    });
    this.setState({
      values: new_state
    });
  }

  componentDidUpdate(prevProps) {
    if (this.props.values != prevProps.values) {
      this.setState({
        values: this.props.values,
      });
    }
  }

  render() {
    return (
      <div className="cluster-schematic">
      <ClusterNetworkCanvas />
      {
          this.state.values.map((row, row_index) => {
              return (
                  <div key={row_index} className="cluster-row">
                  {
                      row.map((val, col_index) => {
                          return (
                                <ClusterCore
                                  key={(row_index + 1)*(col_index + 1)}
                                  value={val}
                                />
                          );
                      })
                  }
                  </div>
              );
          })
      }
    </div>
    );
  }
}

ReactDOM.render(
  <Layout dataUrl={"/cluster/activity"} />,
  document.getElementById('root')
);
