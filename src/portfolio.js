import React from 'react';
//import './Custom.css';


/*function PortfolioBanner() {
  return (
    <section className="ud-page-banner">
      <div className="container">
        <div className="row">
          <div className="col-lg-12">
            <div className="ud-banner-content">
              <h1>Portfolio</h1>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}*/

function StockTable({ stocks, grandTotal /*,userCash*/ }) {
  return (
    <section id="about" className="ud-about">
      <div className="container">
        <div className="ud-about-wrapper">
          <table className="table table-striped table-rounded">
            <thead align="left">
                <tr >
                 <th colSpan={5}  className="stock-holdings" >Stock Holdings</th>
                 <th className="stock-holdings">Account Balance</th>
                 <th className="stock-holdings">Total Value</th>
                </tr> 
              <tr className='border-row' >
                <th>Company</th>
                <th>Shares Count</th>
                <th>By Average</th>
                <th>Recent Close Price</th>
                <th>Market value</th>
                <th>Profit/Loss</th>
                <th>Profit Percentage</th>
              </tr>
            </thead>
            <tbody align="left">
              {stocks.map((stock, index) => {
                const profitLoss = stock.shares * (stock.price - stock.averagePrice);
                const profitPercentage = ((stock.price - stock.averagePrice) / stock.averagePrice) * 100;

                return (
                  <tr key={index}>
                    <td>{stock.company}</td>
                    <td>{stock.shares}</td>
                    <td>{stock.averagePrice}</td>
                    <td>{stock.closePrice}</td>
                    <td>{stock.price}</td>
                    <td>{profitLoss}</td>
                    <td>{profitPercentage.toFixed(2)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export { StockTable, };
