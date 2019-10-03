var DataFrame = require('dataframe-js').DataFrame;
//var  df_1 =   new DataFrame.fromCSV('https://raw.githubusercontent.com/GIScience/openrouteservice-examples/master/resources/data/idai_health_sites.csv');

//DataFrame.fromCSV('https://raw.githubusercontent.com/GIScience/openrouteservice-examples/master/resources/data/idai_health_sites.csv')
//    .then(df=>df);

// The fromCSV method returns a promise so it is placed in this async function for demostration
// The file here is from the Open Route Serivce page demo
async function printdf(){
const x = await DataFrame.fromCSV('https://raw.githubusercontent.com/GIScience/openrouteservice-examples/master/resources/data/idai_health_sites.csv');
console.log("\nLogging the object to the terminal prints the object.\n\n");
console.log(x);
console.log("\nThe show function provides a string repesentation.\n\n");
x.show();
return x;
};
     
printdf();

// This is a mix of example code from the API document
const df_2 = new DataFrame([
    {c1: 1, c2: 6}, // <------- A row
    {c4: 1, c3: 2}
], ['c1', 'c2', 'c3', 'c4']);

    const filteredDf = df_2
        .select("c1", "c2");
    filteredDf.show(1);