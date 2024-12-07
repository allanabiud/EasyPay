const centerLabelPlugin = {
  id: "centerLabel",
  beforeDraw: function (chart) {
    var ctx = chart.ctx;
    var width = chart.width,
      height = chart.height;

    // Calculate the total deduction (you can replace this with your own logic)
    const totalValue = chart.data.datasets[0].data
      .reduce((acc, curr) => acc + curr, 0)
      .toFixed(2);

    // Split the value into integer and decimal parts
    const [integerPart, decimalPart] = totalValue.split(".");

    // Format the integer part with commas for thousands
    const formattedInteger = parseInt(integerPart).toLocaleString();

    // Combine the formatted integer part with the decimal part
    const formattedValue = `${formattedInteger}.${decimalPart}`;

    // Set the font size dynamically based on chart size (optional, adjust divisor for scaling)
    const fontSize = Math.min(width, height) / 16; // Adjust font size proportionally
    ctx.save();
    ctx.font = `bold ${fontSize}px Arial`;
    ctx.fillStyle = "#000000"; // Text color
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    // Draw "Total Deduction" and the value on separate lines
    const labelText = "Total:";
    const valueText = "KES " + formattedValue;

    // Calculate Y positions for text to avoid overlap
    const labelY = height / 2 - fontSize / 2 - 20;
    const valueY = height / 2 + fontSize / 2 - 20;

    // Draw the label and value
    ctx.fillText(labelText, width / 2, labelY); // "Total Deduction"
    ctx.fillText(valueText, width / 2, valueY); // Deduction value

    ctx.restore();
  },
};

// Register the plugin with Chart.js
Chart.register(centerLabelPlugin);

// Render the allowance donut chart
var ctxAllowance = document
  .getElementById("allowanceDonutChart")
  .getContext("2d");

new Chart(ctxAllowance, {
  type: "doughnut",
  data: {
    labels: allowanceData.labels, // Allowance names
    datasets: [
      {
        label: "Allowances",
        data: allowanceData.values, // Allowance values
        backgroundColor: [
          "#1D537D",
          "#632516",
          "#3626a7",
          "#0d0106",
          "#657ed4",
          "#6c756b",
          "#4B1D59",
          "#db7f67",
        ], // Colors for segments
        borderWidth: 0,
      },
    ],
  },
  options: {
    responsive: true, // Ensures the chart resizes with its container
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
          pointStyle: "circle",
        },
      },
      tooltip: {
        callbacks: {
          label: function (tooltipItem) {
            return tooltipItem.label + ": " + tooltipItem.raw;
          },
        },
      },
    },
    cutout: "70%",
  },
});

// Render the deduction donut chart
var ctxDeduction = document
  .getElementById("deductionDonutChart")
  .getContext("2d");

new Chart(ctxDeduction, {
  type: "doughnut",
  data: {
    labels: deductionData.labels, // Deduction names
    datasets: [
      {
        label: "Deductions",
        data: deductionData.values, // Deduction values
        backgroundColor: [
          "#1D537D",
          "#632516",
          "#3626a7",
          "#0d0106",
          "#657ed4",
          "#6c756b",
          "#4B1D59",
          "#db7f67",
        ], // Colors for segments
        borderWidth: 0,
      },
    ],
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
          pointStyle: "circle",
        },
      },
      tooltip: {
        callbacks: {
          label: function (tooltipItem) {
            return tooltipItem.label + ": " + tooltipItem.raw;
          },
        },
      },
    },
    cutout: "70%",
  },
});
