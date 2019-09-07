function MainPanel(props) {
  const img_src = "simulations/" + props.currentSimulation +
    "/elmeroutput0001-velomagn.png"

  return (
    <img id="result-main-image"
         src={img_src}
         alt="Simulation Main View"
         width="100%" />
  );
}

function SimulationList(props) {
  return (
    props.simulations.map((simulation, rank) => {

      const sim_id = simulation['id'];

      const image_url = "simulations/" + sim_id +
        "/elmeroutput0001-velomagn.png";

      const image_alt = "Simulation " + sim_id + " image";

      const additionalMainClasses =
        props.currentSimulation == sim_id ? " selected" : "";

      const additionalRankingClasses = props.showIndex ? "" : " hidden";

      return (
        <div className={"columns simulation" + additionalMainClasses}
                     key={rank}
                     id={"rank" + (sim_id + 1)}
                     onClick={ () => props.onClick(sim_id) }>

            <div
              className={"ranking column is-one-fifth" + additionalRankingClasses}
            >
            <h2>
              { rank + 1 }
            </h2>
          </div>

          <div className="simulation-data">

            <img src={image_url}
                 alt={image_alt}
                 width="100%" />

            <div className="simulation-info">
              <p>
                {simulation['name']}
              </p>
              <p>
                drag: {simulation['drag'].toFixed(2)}
              </p>
            </div>
          </div>
          </div>
      );
    })
  );
}

class Layout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      bestSimulations: [],
      recentSimulations: [],
      currentSimulation: 1,
      errors: []
    };
  }

  // fetch best simulations from server and update in component state
  simulationFetcher(url, target) {
    fetch(url)
      .then(res => res.json())
      .then(
        (result) => {
          var state = {};
          state[target] = result;

          this.setState(state);
        },
        (error) => {
          this.setState({
            errors: ["failed to load max drag data"]
          });
        }
      );
  }

  fetchBestSimulations() {
    this.simulationFetcher("/simulations/max_drag/10", 'bestSimulations');
  }

  fetchRecentSimulations() {
    this.simulationFetcher("/simulations/recent/10", 'recentSimulations');
  }
  componentDidMount() {
    this.fetchBestSimulations();
    this.fetchRecentSimulations();
  }

  simulationChoiceHandler(sim_id) {
    this.setState({
      currentSimulation: sim_id
    });
  }

  render() {
    return (
      <div className="container">
              <div className="columns">
                <div className="column is-two-thirds is-vertical-centre">
                  <MainPanel currentSimulation={this.state.currentSimulation}/>
                </div>
                <div id="leaderboard" className="column is-scroll">
                  <h2>Leaderboard</h2>
                  <SimulationList showIndex={ true }
                                  simulations={ this.state.bestSimulations }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                </div>
                <div id="recent-simulations" className="column is-scroll">
                  <h2>Recent</h2>
                  <SimulationList showIndex={ false }
                                  simulations={ this.state.recentSimulations }
                                  currentSimulation={this.state.currentSimulation}
                                  onClick={ this.simulationChoiceHandler.bind(this) }/>
                </div>
              </div>
            </div>
    );
  }
}

ReactDOM.render(
  <Layout />,
  document.getElementById('root')
);
