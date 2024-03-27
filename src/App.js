import React from 'react';
import PortfolioMarket from './portfolioMarket';

/*import  { StockTable } from './portfolio.js';*/
import './Custom.css';




function App() {
 /* const stocks = [
    { company: 'ABQK', shares: 160, averagePrice: 2179.96, closePrice: 2.75, price: 440.15 },
    { company: 'AHCS', shares: 70, averagePrice: 2.00, closePrice: 2.21, price: 154.70 }
  ];
  const grandTotal = 3000;
  const userCash = 500; */
    
  return (
    <>
      <div className="App">
        {/*<StockTable stocks={stocks} grandTotal={grandTotal} userCash={userCash} />*/}
        <PortfolioMarket />
        
      </div>
    
    </>
  );
}

export default App;




