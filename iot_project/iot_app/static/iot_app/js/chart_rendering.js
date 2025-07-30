


  // --- HÀM MỚI ĐỂ VẼ BIỂU ĐỒ CPU CHO PI ---

function renderMetricChartFromData(piId, metricType, chartData, chartId, loadingMessageId, labelText, unit) {

      const metricHistoryApiUrl = `/api/raspberry_pi/metric_history_bundle/${piId}/`;
      // Hiển thị thông báo "Đang tải..."
    $(`#${loadingMessageId}`).text(`Đang tải biểu đồ ${labelText}...`).show();

    const canvas = document.getElementById(chartId);

    if (!canvas) {
        console.warn(`Không tìm thấy canvas với ID: ${chartId} sau khi load lại HTML.`);
        return;
    }

     let yAxisMax;
    if (metricType === 'CPU') {
        yAxisMax = 100;
    } else if (metricType === 'RAM') {
        yAxisMax = 32;
    } else if (metricType === 'TEMP') {
        yAxisMax = 100;
    } else {
        yAxisMax = undefined;
    }


    const ctx = canvas.getContext('2d');

    const existingChart = iot_app.charts.chartPiInstances?.[chartId];

     if (existingChart && existingChart.ctx !== ctx) {
        console.log("khong ton tai ctx")
        existingChart.destroy();
        delete iot_app.charts.chartPiInstances[chartId];
       
    }

    // Kiểm tra nếu chart đã tồn tại → chỉ cập nhật dữ liệu
    if (iot_app.charts.chartPiInstances?.[chartId]) 
    {
        console.log("ton tai ctx")
        const chart = iot_app.charts.chartPiInstances[chartId]; 
        chart.data.labels = chartData.labels;
        chart.data.datasets[0].data = chartData.data;
        chart.update();
    } 
    else 
    {
        // Khởi tạo biểu đồ mới nếu chưa có
        if (!iot_app.charts.chartPiInstances) iot_app.charts.chartPiInstances = {};   

        console.log(`load char:${chartId}`)

        iot_app.charts.chartPiInstances[chartId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: `${labelText} (${chartData.unit || unit})`,
                    data: chartData.data,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: false, // Tối ưu hiệu năng
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: yAxisMax,
                        title: {
                            display: true,
                            text: `${labelText} (${chartData.unit || unit})`
                        }
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 10
                        },
                        title: {
                            display: true,
                            text: 'Thời gian'
                        }
                    }
                },
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: { mode: 'index', intersect: false }
                }
            }
        });
    }

    // Ẩn loading khi xong
    $(`#${loadingMessageId}`).hide();
}

/**************/

function crreate_dataset(data, sensor_type)
{
    if(sensor_type=='temperature')
    {
        return {
            label: 'Nhiệt độ (°C)',
            data: data,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            tension: 0.3,
            parsing: {
                xAxisKey: 'x',
                yAxisKey: 'y'
            },
            sensor_type: sensor_type,
        }
    }
    else if(sensor_type=='sound')
    {
        return {
            label: 'Âm thanh (dB)',
            data: data,
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            tension: 0.3,
            parsing: {
                xAxisKey: 'x',
                yAxisKey: 'y'
            },
            sensor_type: sensor_type,
        }
    }
    else if(sensor_type=='vibration')
    {
        return {
            label: 'Rung (vibration)',
            data: data,
            borderColor: 'rgba(255, 206, 86, 1)',
            backgroundColor: 'rgba(255, 206, 86, 0.2)',
            tension: 0.3,
            parsing: {
                xAxisKey: 'x',
                yAxisKey: 'y'
            },
            sensor_type:sensor_type,
        }
    }
    else
    {
        return None;
    }
}

function init_render_data(chartData)
{
    const datasets = [];

    if (chartData.temperature && chartData.temperature.length > 0) {
        datasets.push(crreate_dataset(chartData.temperature,'temperature'));
    }

    if (chartData.sound && chartData.sound.length > 0 ) {
        datasets.push(crreate_dataset(chartData.sound,'sound'));
    }

    if (chartData.vibration &&  chartData.vibration.length > 0 ) {
        datasets.push(crreate_dataset(chartData.sound,'vibration'));

    }

    return datasets
}


function renderCombinedChart(chartData,chartId) {
    
    const canvas = document.getElementById(chartId);
    const ctx = canvas.getContext('2d');
    const existingChart = iot_app.charts.chartSensorInstances?.[chartId];  
    
    if (existingChart && existingChart.ctx !== ctx) {
        console.log("khong ton tai ctx")
        existingChart.destroy();
        delete iot_app.charts.chartSensorInstances[chartId];
    }
    // Kiểm tra nếu chart đã tồn tại → chỉ cập nhật dữ liệu

    if (iot_app.charts.chartSensorInstances?.[chartId]) 
    {
        console.log("ton tai ctx")
        const chart = iot_app.charts.chartSensorInstances[chartId];
        console.log(`old datasets:${chart.data.datasets}`)

        const existingTypes = chart.data.datasets.map(ds => ds.sensor_type);
        console.log("Các sensor_type hiện tại:", existingTypes);

        const newDatasets = {
            'temperature': chartData.temperature,
            'sound': chartData.sound,
            'vibration': chartData.vibration
        };

        chart.data.datasets.forEach((dataset) => {
            
            const type = dataset.sensor_type; // custom field bạn đã gắn
            if (newDatasets[type]) {
                console.log(`load ${type}`)
                dataset.data = newDatasets[type];
            }
            else {
                dataset.data = [];  // hoặc giữ nguyên cũ nếu bạn muốn
                console.log(`Không có dữ liệu cho ${type}, set về []`);
            }
        });


        for (const type in newDatasets) {
            console.log(type)

            if (!existingTypes.includes(type)) {
                if (Array.isArray(newDatasets[type]) && newDatasets[type].length > 0)
                {
                    console.log(`Thêm mới dataset: ${type}`);
                    chart.data.datasets.push(crreate_dataset(newDatasets[type],type));
                }
            }
        }
        chart.update();
    } 
    else 
    {
        // Khởi tạo biểu đồ mới nếu chưa có
        if (!iot_app.charts.chartSensorInstances) iot_app.charts.chartSensorInstances = {};

        console.log('khoi tao bieu do moi')

        const datasets = init_render_data(chartData);

        iot_app.charts.chartSensorInstances[chartId] = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: datasets
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                stacked: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Biểu đồ tổng hợp cảm biến'
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            tooltipFormat: 'yyyy-MM-dd HH:mm',
                            displayFormats: {
                                minute: 'HH:mm',
                                hour: 'HH:mm',
                                day: 'dd-MM'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Thời gian'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Giá trị đo'
                        },
                        beginAtZero: true
                    }
                }
            }
        });
    }
}





