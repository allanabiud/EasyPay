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
          "#1D537D", // Dark Blue
          "#632516", // Dark Red
          "#3626a7", // Dark Purple
          "#0d0106", // Very Dark Brown
          "#657ed4", // Light Blue
          "#6c756b", // Olive Green
          "#4B1D59", // Deep Pink
          "#db7f67", // Soft Orange
        ].map((color) => hexToRgba(color, 0.8)), // Apply 0.8 transparency
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
    hover: {
      mode: "nearest", // Ensures the hover is detected on the nearest segment
      animationDuration: 300, // Smooth animation on hover
      onHover: function (event, chartElement) {
        const chart = this.chart;
        const dataset = chart.data.datasets[0];

        // Reset all segments to normal size
        dataset.borderWidth = 0;

        // If a segment is hovered, increase its size
        if (chartElement.length > 0) {
          const segmentIndex = chartElement[0].index;
          const segment = chartElement[0];

          // Increase the size of the hovered segment by adjusting radius
          segment.radius = segment._model.fullRadius * 1.2; // 20% larger on hover
          segment.borderWidth = 2; // Optional: border width increase on hover
        }

        // Update chart to reflect changes
        chart.update();
      },
      onLeave: function (event, chartElement) {
        const chart = this.chart;
        const dataset = chart.data.datasets[0];

        // Reset radius and border width when hover ends
        dataset.data.forEach(function (data, index) {
          const segment = chart.getDatasetMeta(0).data[index];
          segment.radius = segment._model.fullRadius; // Reset to original radius
          segment.borderWidth = 0; // Reset border width
        });

        // Update chart to reflect reset changes
        chart.update();
      },
    },
    animation: {
      animateScale: true, // Animate the scale when hovering
      animateRotate: true, // Animate rotation
    },
    elements: {
      arc: {
        borderWidth: 2,
        borderColor: "#fff", // Optional: adds a border to the segments
      },
    },
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
          "#1D537D", // Dark Blue
          "#632516", // Dark Red
          "#3626a7", // Dark Purple
          "#0d0106", // Very Dark Brown
          "#657ed4", // Light Blue
          "#6c756b", // Olive Green
          "#4B1D59", // Deep Pink
          "#db7f67", // Soft Orange
        ].map((color) => hexToRgba(color, 0.8)), // Apply 0.8 transparency
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
    hover: {
      mode: "nearest", // Ensures the hover is detected on the nearest segment
      animationDuration: 300, // Smooth animation on hover
      onHover: function (event, chartElement) {
        const chart = this.chart;
        const dataset = chart.data.datasets[0];

        // Reset all segments to normal size
        dataset.borderWidth = 0;

        // If a segment is hovered, increase its size
        if (chartElement.length > 0) {
          const segmentIndex = chartElement[0].index;
          const segment = chartElement[0];

          // Increase the size of the hovered segment by adjusting radius
          segment.radius = segment._model.fullRadius * 1.2; // 20% larger on hover
          segment.borderWidth = 2; // Optional: border width increase on hover
        }

        // Update chart to reflect changes
        chart.update();
      },
      onLeave: function (event, chartElement) {
        const chart = this.chart;
        const dataset = chart.data.datasets[0];

        // Reset radius and border width when hover ends
        dataset.data.forEach(function (data, index) {
          const segment = chart.getDatasetMeta(0).data[index];
          segment.radius = segment._model.fullRadius; // Reset to original radius
          segment.borderWidth = 0; // Reset border width
        });

        // Update chart to reflect reset changes
        chart.update();
      },
    },
    animation: {
      animateScale: true, // Animate the scale when hovering
      animateRotate: true, // Animate rotation
    },
    elements: {
      arc: {
        borderWidth: 2,
        borderColor: "#fff", // Optional: adds a border to the segments
      },
    },
  },
});

// Function to convert hex color to RGBA (with transparency)
function hexToRgba(hex, alpha = 0.8) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`; // Less transparent with alpha = 0.8
}
