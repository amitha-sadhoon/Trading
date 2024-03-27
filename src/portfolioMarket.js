import React from "react";

function PortfolioMarket() {
  return (
    <div>
      <div className="container-fluid">
        <div className="row">
          {/* Main Content (Second Column) */}
          <div className="col-md-9 vh-100 main-content d-flex flex-column">
            {/* First Row in Second Column (Top-aligned) */}
            <div className="card" style={{ background: 'linear-gradient(to right, #010000, #761917)' }}>
              <div className="card-body" id="overall-market" style={{ padding: '0.5rem' }}>
                <div className="row justify-content-center">
                  <div className="col-3">
                    <a href="/" style={{ textDecoration: 'none' }}>
                      <img src="s-treasury.png" style={{ maxWidth: 70 }} alt="Logo" />
                    </a>
                  </div>
                  <div className="col-3">
                    <h6 style={{ color: 'white' }}>Index:<span id="index-value" style={{ color: '#e4c55a', paddingLeft: 2 }}>0</span></h6>
                  </div>
                  <div className="col-3">
                    <h6 style={{ color: 'white' }}>Volume:<span id="total-volume" style={{ color: '#e4c55a', paddingLeft: 2 }}>0</span></h6>
                  </div>
                  <div className="col-3">
                    <h6 style={{ color: 'white' }}>Change:<span id="percentage-change" style={{ color: '#e4c55a', paddingLeft: 2 }}>0</span> %</h6>
                  </div>
                </div>
              </div>
            </div>
            {/*<div class="card flex-grow-1">*/}
            {/*    <div class="card-body">*/}
            {/* TradingView Chart */}
            <div className="tradingview-widget-container" style={{ height: '100%' }}>
              <div id="tradingview-widget" style={{ height: '100%' }}>Please wait While Loading Chart</div>
            </div>
            {/*    </div>*/}
            {/*</div>*/}
            {/* Third Row in Second Column (Bottom-aligned) --==========> */}

            <div className="card">
              <div className="card-header">
                <div className="row">
                  <div className="col-9">
                    {/* <div class="tabbable-panel"> */}
                    <div className="tabbable-line">
                      <ul className="nav nav-tabs ">
                        <li className="nav-item">
                          <a className="nav-link active" data-toggle="tab" href="#tab_stocks">Stocks</a>
                        </li>
                        <li className="nav-item">
                          <a className="nav-link" data-toggle="tab" href="#tab_orders">Orders</a>
                        </li>
                        <li className="nav-item">
                          <a className="nav-link" data-toggle="tab" href="#tab_portfolio">Portfolio</a>
                        </li>
                        <li className="nav-item">
                          <a className="nav-link" data-toggle="tab" href="#tab_trade">Trade <i className="fas fa-circle fa-xs" style={{ color: 'rgb(34, 150, 34)' }} /></a>
                        </li>
                      </ul>
                    </div>
                    {/* </div> */}
                  </div>
                  <div className="col-2 text-right">
                    <button id="toggle-options" className="btn btn-sm nav-link" onclick="toggleBuySellOptions()">
                      <i id="options-icon" className="fas fa-chevron-up" />
                      <span id="options-text">Show Options</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            {/* Buy/Sell Options (Initially hidden) */}
            <div className="mt-auto buy-sell-options" id="buy-sell-options" style={{ maxHeight: 300, minHeight: 200, overflow: 'auto', display: 'none', padding: 0 }}>
              <div className="tab-content">
                <div className="tab-pane active" id="tab_stocks" style={{ padding: 0 }}>
                  <div className="row">
                    <div className="container">
                      <table className="table table-bordered table-hover table-fixed">
                        <thead>
                          <tr>
                            <th style={{ width: '20%' }}>COMPANY</th>
                            <th>PRICE</th>
                            <th>CHG</th>
                            <th>CHG%</th>
                            <th>RATING</th>
                            <th>VOLUME</th>
                            <th style={{ width: '20%' }}>INDUSTRY</th>
                          </tr>
                        </thead>
                        <tbody id="stocks-table-body">
                          {/* Existing rows will be replaced by JavaScript */}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div className="tab-pane" id="tab_orders">
                  <div className="card-header">
                    <div className="row">
                      {/* <div class="tabbable-panel"> */}
                      <div className="tabbable-line">
                        <ul className="nav nav-tabs ">
                          <li className="nav-item">
                            <a className="nav-link active" data-toggle="tab" href="#tab_pending_order">Pending</a>
                          </li>
                          <li className="nav-item">
                            <a className="nav-link" data-toggle="tab" href="#tab_completed_order">Completed</a>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PortfolioMarket;


