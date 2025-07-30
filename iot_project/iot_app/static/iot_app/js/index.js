 ////////////////////////////////////////////////////////////////////////////////////////////////////////////
 // 

function formatLocalDatetime(isoString) {
    const d = new Date(isoString);
    return d.toLocaleString('vi-VN', {
        hour12: false,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

function getISOStringOffsetHours(hoursAgo) {
        const now = new Date();
        const past = new Date(now.getTime() - hoursAgo * 60 * 60 * 1000);
        return [past.toISOString(), now.toISOString()];
}

const updateNodeWithServerRenderedHtml = function(nodeId, newHtmlContent){

    const treeInstance = $('#main-tree').jstree(true);
    const existingNode = treeInstance.get_node(nodeId);

    if (existingNode) {
        // Cập nhật text của node trong jsTree
        treeInstance.set_text(nodeId, newHtmlContent);
    } else {
        // console.warn(`Node with ID ${nodeId} not found for update.`);
    }
};


const fetchLatestSensorHtmlUpdates = function() {
          /*Lấy vị trí cuộn*/
    const treeScrollContainer = $('#main-tree');
    const scrollTopPosition = treeScrollContainer.scrollTop();
    const scrollTopPositionWindow = $(window).scrollTop();

    const selectedId = $('#main-tree').attr('data-selected-id');
    const selectedType = $('#main-tree').attr('data-selected-type');

    $.ajax({
        url: "/api/sensor-updates/", 
        method: 'GET',
        dataType: 'json', // Mong đợi JSON phản hồi (list các {id, html})
        success: function(response){
            // response sẽ là một mảng các đối tượng: [{ id: 'sensor_1', html: '<img ...>Sensor: ... Value: ...' }, ...]
            response.forEach( function(nodeUpdate){
                updateNodeWithServerRenderedHtml(nodeUpdate.id, nodeUpdate.html);

                if (selectedType === 'sensor' && nodeUpdate.id === selectedId) {
                    // Parse nodeUpdate.html để tách phần info cần cập nhật
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(nodeUpdate.html, 'text/html');
                    updateSensorDetailFromTree(doc);
                }


            });
            //Khôi phục vị trí cuộn
            treeScrollContainer.scrollTop(scrollTopPosition);
            $(window).scrollTop(scrollTopPositionWindow);
        },
        error: function(jqXHR, textStatus, errorThrown){
            console.error("Lỗi khi tải cập nhật cảm biến:", textStatus, errorThrown);
        }
    });
};


function loadPiCharts(nodeId)
{
    $.getJSON(`/api/raspberry_pi/metric_history_bundle/${nodeId}/`, function(result) {
            ['CPU', 'RAM', 'TEMP'].forEach(function(metric) {
                const config = {
                    CPU: { chartId: 'cpuUsageChart', loadingId: 'cpuChartLoadingMessage', label: 'CPU Usage', unit: '%' },
                    RAM: { chartId: 'ramUsageChart', loadingId: 'ramChartLoadingMessage', label: 'RAM Usage', unit: 'GB' },
                    TEMP: { chartId: 'tmperatureChart', loadingId: 'temperatureChartLoadingMessage', label: 'CPU Temp', unit: '°C' }
                }[metric];

                renderMetricChartFromData(
                    nodeId,
                    metric,
                    result[metric],
                    config.chartId,
                    config.loadingId,
                    config.label,
                    config.unit
                );
            });
        });
}

function loadPiInfoAndMonitor(nodeId)
{
        $.get(`/api/raspberry_pi/info_and_monitor_partial/${nodeId}/`, function(response) {
            $('#raspi-info-container').html(response.info_html);
            $('#raspi-status-container').html(response.monitor_html);
        });   
}


/******/
function loadEspSensor(nodeId)
{
    $.get(`/api/esp/sensors/${nodeId}/`, function(response) {
        
        console.log("--ajax load esp sensor---")
        $('#esp-sensors-container').html(response.html);
    });   
}

function loadEspCharts(nodeId,startTime,endTime)
{
    $.getJSON(`/api/esp/charts/${nodeId}/`, { start: startTime, end: endTime },function(result) {
            console.log("--ajax load esp charts---")
            renderCombinedChart(result,'esp-charts');
            
        });
}

/******/

function loadSensorCharts(nodeId,startTime,endTime)
{
    $.getJSON(`/api/sensor/charts/${nodeId}/`, { start: startTime, end: endTime }, function (result) {
     
        console.log("cap nhap cam bien");
        renderCombinedChart(result,'js-sensor-detail-tabs-chart');
    
    });
}

function loadSensorDataTable(nodeId) {
    
    if (!$.fn.DataTable.isDataTable('#sensor-data-table')) 
    {
        iot_app.sensor_node.table_filter.event='init';
        iot_app.sensor_node.table_filter.column_default='timestamp_device' 
        
        $('#sensor-data-table').DataTable({
            processing: true,
            serverSide: true,
            search:false,
            ajax: {
                url: `/api/sensor/table/${nodeId}/`,
                data: function (d) {
                     Object.assign(d, iot_app.sensor_node.table_filter);
                },
                dataSrc: 'data'
            },
            pageLength: 10, 
            columns: [
                { data: 'index' },
                { 
                    data: 'timestamp_device',
                    render: function(data, type, row){
                        return formatLocalDatetime(data);
                    }
                },
                { data: 'value' },
                { data: 'sensor_type', orderable: false},
                { 
                    data:'timestamp_server',
                    render: function(data, type, row){
                        return formatLocalDatetime(data);
                    }
                }
            ],

            order: [[1, 'desc']],

            destroy: true,

            dom: 'Bfrtip', 

            buttons: [
                {
                    extend: 'copy',
                    text: '<i class="fas fa-copy"></i> Sao chép',
                    className: 'btn-copy'
                },
                {
                    extend: 'csv',
                    text: '<i class="fas fa-file-csv"></i> CSV',
                    className: 'btn-csv'
                },
                {
                    extend: 'excel',
                    text: '<i class="fas fa-file-excel"></i> Excel',
                    className: 'btn-excel'
                },
                {
                    extend: 'pdf',
                    text: '<i class="fas fa-file-pdf"></i> PDF',
                    className: 'btn-pdf'
                },
                {
                    extend: 'print',
                    text: '<i class="fas fa-print"></i> In',
                    className: 'btn-print'
                }
            ],
            createdRow: function (row, data, dataIndex) {
                 // Ví dụ: ngưỡng cảnh báo là 60
                const sensorType = data.sensor_type;
                let threshold = null;
                if(sensorType=='temperature')
                {
                    threshold=50;
                }
                else if(sensorType=='sound')
                {
                    threshold=4000;
                }
                else if(sensorType=='vibration')
                {
                    threshold=3000;
                }

                if(threshold)
                {
                    if (parseFloat(data.value) > threshold) {
                        // Thêm class cảnh báo vào toàn bộ dòng
                        $(row).addClass('row-warning');
                    }
                }
            },
            initComplete: function () {
                // Di chuyển các nút buttons vào container đã tạo
                this.api().buttons().container().appendTo('#sensor-data-buttons');
            }
        });
    } 
    else 
    {
        $('#sensor-data-table').DataTable().ajax.reload();
    }
}

function updateSensorDetailFromTree(doc) {

    const div = doc.querySelector('.jstree__sensor-node');

    // Lấy giá trị từ các data-attributes
    const sensorName = div.getAttribute('data-sensor-name');
    const latestValue = div.getAttribute('data-latest-value');
    const sensorType = div.getAttribute('data-sensor-type');
    const latestDate=div.getAttribute('data-latest-date');
    const local_latestDate=formatLocalDatetime(latestDate)
    const status=div.getAttribute('data-sensor-status');

    console.log(latestValue)
    console.log(`latestDate=${latestDate}`)
    console.log(`local_latestDate=${local_latestDate}`)
    console.log(status)

    document.getElementById('sensor-detail-info-value').textContent = latestValue;
    document.getElementById('sensor-detail-info-lastest-time').textContent = local_latestDate;

    const statusDot = document.getElementById('js-sensor-status-dot');
    const statusText = document.getElementById('js-sensor-status-text');

    if (status === 'True' || status === true) {
        statusDot.style.backgroundColor = 'green';
        statusText.textContent = 'Đang hoạt động';
    } else {
        statusDot.style.backgroundColor = 'red';
        statusText.textContent = 'Không hoạt động';
    }
}

/******/

function esp_off_auto_update()
{
    if (iot_app.esp_node.EspAutoUpdateInterval)
    {
        console.log('stop EspAutoUpdateInterval')
        clearInterval(iot_app.esp_node.EspAutoUpdateInterval);
        iot_app.esp_node.EspAutoUpdateInterval = null;
    }

     if (iot_app.esp_node.EspAutoUpdateInterval2)
    {
        console.log('stop EspAutoUpdateInterval2')
        clearInterval(iot_app.esp_node.EspAutoUpdateInterval2);
        iot_app.esp_node.EspAutoUpdateInterval2 = null;
    }
}

function pi_off_auto_update()
{
    if(iot_app.pi_node.PiAutoUpdateInterval) 
    {
        console.log('stop PiAutoUpdateInterval')
        clearInterval(iot_app.pi_node.PiAutoUpdateInterval);
        iot_app.pi_node.PiAutoUpdateInterval = null;
    }

}

function sensor_off_auto_update()
{
    if (iot_app.sensor_node.SensorAutoUpdateInterval)
    {
        console.log('stop SensorAutoUpdateInterval')
        clearInterval(iot_app.sensor_node.SensorAutoUpdateInterval);
        iot_app.sensor_node.SensorAutoUpdateInterval = null;
    }
}

function offAutoupdate()
{
    pi_off_auto_update();

    esp_off_auto_update();

    sensor_off_auto_update();
}

/******/

function ProcessNodeRaspberry(nodeId)
{
    loadPiCharts(nodeId);
    loadPiInfoAndMonitor(nodeId);

    if(!iot_app.pi_node.PiAutoUpdateInterval )
    {
        iot_app.pi_node.PiAutoUpdateInterval = setInterval(function () {
            loadPiCharts(nodeId);
            loadPiInfoAndMonitor(nodeId);
        }, 5000);
    }
}

/******/
/*****/
function loadDeviceDetailFromTree(nodeId) {
    const tree = $('#main-tree').jstree(true);  // lấy instance jsTree
    if (tree) {
        tree.deselect_all(); // bỏ chọn trước (tuỳ chọn)
        tree.select_node(nodeId);  // chọn node theo id
    }
}
/********************/


function ProcessNodeEsp32(nodeId)
{
     
    $("#esp_tabs").tabs({
            active: 0, // Kích hoạt tab đầu tiên ngay lập tức
            activate: function (event, ui) {
                const newIndex = ui.newTab.index();  // Lấy index tab mới được kích hoạt

                console.log("thay dổi tab");
                esp_off_auto_update();
                            
                if (newIndex === 2) {  // Tab thứ 3 (đếm từ 0)
                    console.log('tab 2')
                    const [start, end] = getISOStringOffsetHours(24);
                    loadEspCharts(nodeId,start,end);  // Gọi hàm AJAX để tải biểu đồ
                    $('#esp-charts-checkbox-update').prop('checked', false);
                     iot_app.esp_node.espCheckboxBound   = false;
                }
                else if(newIndex==1)
                {
                    console.log('tab1')
                    loadEspSensor(nodeId);
                    $('#esp-sensors-checkbox-update').prop('checked',false);
                }
            }
        });



        /*esp-charts*/

         $("#esp-detail-tabs-buttons-24h").on("click", function () {
            const [start, end] = getISOStringOffsetHours(24);
            console.log(`${start} - ${end}`)
            loadEspCharts(nodeId, start, end);
        });


        $("#esp-detail-tabs-buttons-7day").on("click", function () {
            const [start, end] = getISOStringOffsetHours(24 * 7);
            loadEspCharts(nodeId, start, end);
        });

        $("#esp-detail-tabs-buttons-30day").on("click", function () {
            const [start, end] = getISOStringOffsetHours(24 * 30);
            loadEspCharts(nodeId, start, end);
        });

        
        $("#esp-detail-tabs-buttons-option").on("click", function () {

            console.log('---esp-buttons-option-click---')
            
            const startInput = $("#esp-detail-tabs-buttons-option-start-date").val();
            const endInput = $("#esp-detail-tabs-buttons-option-end-date").val();

            console.log(`local: ${startInput}- ${endInput}`)
       
            if (startInput && endInput) {
                const start = new Date(startInput).toISOString();
                const end = new Date(endInput).toISOString();
                console.log(`uct: ${start}-${end}`)
                loadEspCharts(nodeId, start, end);
            } else {
                alert("Vui lòng chọn đầy đủ thời gian bắt đầu và kết thúc.");
            }
        });

        if (! iot_app.esp_node.espCheckboxBound  )  
        {
            $('#sensor-toggles').on('change', 'input[type="checkbox"]', function () {
                
                const chart = iot_app.charts.chartSensorInstances['esp-charts']; 
                const sensorType = $(this).val();
                const checked = $(this).is(':checked');
                chart.data.datasets.forEach((dataset) => {

                    if (dataset.sensor_type === sensorType) {
                        
                        console.log(`ẩn ${sensorType}`)

                        dataset.hidden = !checked;
                    }
                });
                chart.update();
            });

             iot_app.esp_node.espCheckboxBound   = true; // Đánh dấu đã gắn event
        }

        $('#esp-charts-checkbox-update').on('change', function () {
        
            console.log('esp-charts-checkbox-update: event- change')

            if ($(this).is(':checked')) {

                if (!iot_app.esp_node.EspAutoUpdateInterval)
                {
                    alert("Đã bật tự cập nhập mỗi 5s");
                    const [start, end] = getISOStringOffsetHours(24);
                    iot_app.esp_node.EspAutoUpdateInterval=setInterval(() => {
                        loadEspCharts(nodeId,start, end); 
                    }, 5000);
                }
            
            } else 
            {
                alert("Đã tắt tự cập nhập");
                console.log('EspAutoUpdateInterval: stop')
                clearInterval(iot_app.esp_node.EspAutoUpdateInterval);
                iot_app.esp_node.EspAutoUpdateInterval = null;
            }
        });

        /*esp-sensors */
         $('#esp-sensors-checkbox-update').on('change', function () {
        
            console.log('esp-sensors-checkbox-update: event- change')

            if ($(this).is(':checked')) {

                if (!iot_app.esp_node.EspAutoUpdateInterval2)
                {
                    alert("Đã bật tự cập nhập mỗi 5s");
                    iot_app.esp_node.EspAutoUpdateInterval2=setInterval(() => {
                        loadEspSensor(nodeId);
                    }, 5000);
                }
            
            } else 
            {
                alert("Đã tắt tự cập nhập");
                console.log('EspAutoUpdateInterval2: stop')
                clearInterval(iot_app.esp_node.EspAutoUpdateInterval2);
                iot_app.esp_node.EspAutoUpdateInterval2 = null;
            }
        });


        $(document).on('click', '.view-details-button', function () {
            var sensorId = $(this).data('sensor-id');
            console.log("Sensor ID:", sensorId);
            loadDeviceDetailFromTree(sensorId)
        });
}

/******/

function ProcessNodeSensor(nodeId)
{

    /*giao diện tab*/
    $("#sensor-detail-tabs").tabs({
            
        active: 0, // Kích hoạt tab đầu tiên ngay lập tức

            activate: function (event, ui) {
              
                const newIndex = ui.newTab.index();  // Lấy index tab mới được kích hoạt

                if (newIndex === 0)
                {
                    console.log('kích hoạt tab 0');   
                    const [start, end] = getISOStringOffsetHours(24);
                    loadSensorCharts(nodeId, start, end);
                }

                else if (newIndex === 1) {
                    console.log('kích hoạt tab 1 - dữ liệu');
                    loadSensorDataTable(nodeId);  // Gọi hàm khởi động bảng dữ liệu

                }

                if (!ui.newPanel.is("#sensor-detail-tabs-setting-control")) {
                    // Nếu rời khỏi tab Cài đặt → xóa message
                    $("#js-sensor-setting-wrapper .message").remove();
                }
        
            }
        });

        /*kiem tra tab kích hoạt khi load lần đầu */

        const activeIndex = $("#sensor-detail-tabs").tabs("option", "active");
        
        if (activeIndex === 0) {
            const [start, end] = getISOStringOffsetHours(24);
            loadSensorCharts(nodeId, start, end);
        }
        
        
        /**tab biểu đồ: tab 0*/
        $("#sensor-detail-tabs-buttons-24h").on("click", function () {
            const [start, end] = getISOStringOffsetHours(24);
            console.log(`${start} - ${end}`)
            loadSensorCharts(nodeId, start, end);
        });


        $("#sensor-detail-tabs-buttons-7day").on("click", function () {
            const [start, end] = getISOStringOffsetHours(24 * 7);
            loadSensorCharts(nodeId, start, end);
        });

        $("#sensor-detail-tabs-buttons-30day").on("click", function () {
            const [start, end] = getISOStringOffsetHours(24 * 30);
            loadSensorCharts(nodeId, start, end);
        });

        
        $("#sensor-detail-tabs-buttons-option").on("click", function () {
        const startInput = $("#sensor-detail-tabs-buttons-option-start-date").val();
        const endInput = $("#sensor-detail-tabs-buttons-option-end-date").val();

        if (startInput && endInput) {
            const start = new Date(startInput).toISOString();
            const end = new Date(endInput).toISOString();
            console.log(`tùy chọn: ${start}-${end}`)
            loadSensorCharts(nodeId, start, end);
        } else {
            alert("Vui lòng chọn đầy đủ thời gian bắt đầu và kết thúc.");
        }
        });


        $("#sensor-detail-tabs-checkbox-update").on('change', function () {
        
            console.log('sensor-detail-tabs-checkbox-update: event- change')

            if ($(this).is(':checked')) {

                if (!iot_app.sensor_node.SensorAutoUpdateInterval)
                {
                    alert("Đã bật tự cập nhập mỗi 5s");
                    const [start, end] = getISOStringOffsetHours(24);
                    iot_app.sensor_node.SensorAutoUpdateInterval=setInterval(() => {
                        loadSensorCharts(nodeId,start, end); 
                    }, 5000);
                }
            
            } else 
            {
                alert("Đã tắt tự cập nhập");
                console.log('SensorAutoUpdateInterval: stop')
                clearInterval(iot_app.sensor_node.SensorAutoUpdateInterval);
                iot_app.sensor_node.SensorAutoUpdateInterval = null;
            }
        });

        /*tab dư liệu tab 1*/

        $("#sensor-data-form-search-btn-search").on('click', function () {
            
            console.log('sensor-data-form-search-btn-search: click')

            const start = $("#sensor-data-form-search-from_date").val();
            const stop =  $("#sensor-data-form-search-to_date").val();


            if (start && stop)
            {
                // Cập nhật global filter
                iot_app.sensor_node.table_filter.start_date = new Date(start).toISOString()
                iot_app.sensor_node.table_filter.stop_date =  new Date(stop).toISOString()
                iot_app.sensor_node.table_filter.event = "filter";
                $('#sensor-data-table').DataTable().page(0).draw(false);
            }
            else
            {
                alert("Vui lòng chọn đầy đủ thời gian bắt đầu và kết thúc.");
            }
           
        });


        $("#sensor-data-form-search-btn-reset").on('click', function () {
        
            console.log('sensor-data-form-search-btn-reset: click')

            $("#sensor-data-form-search-from_date").val('');
            $("#sensor-data-form-search-to_date").val('');

            iot_app.sensor_node.table_filter.start_date = null
            iot_app.sensor_node.table_filter.stop_date =  null
            iot_app.sensor_node.table_filter.event = "init";

            $('#sensor-data-table').DataTable().search(''); 
            
            $('#sensor-data-table').DataTable().page(0).draw(false);        
        });


        //ta phải dùng documet để bắt sự kiện trên form vì khi ajax form sẽ thay đổi và xóa liên kết với fomr
        $(document).on("submit", "#js-sensor-setting-form", function(e) {
                e.preventDefault();  // chặn gửi form thật
                console.log("form submit");
                var $form = $(this);

                $.ajax({
                    type: "POST",
                    url: $form.attr("action"),
                    data: $form.serialize(), // tự gom input
                    success: function(response) {
                        $("#js-sensor-setting-wrapper").html(response.html);
                    },
                    error: function() {
                        alert("Lỗi khi gửi dữ liệu!");
                    }
                });
        });

}

/******/

function processDetailContent(nodeType,nodeId){

    offAutoupdate();

    if (nodeType=='raspberry_pi')
    {
        ProcessNodeRaspberry(nodeId);
    
    }
    else if (nodeType=='esp_device')
    {
       ProcessNodeEsp32(nodeId);

    }
    else if (nodeType=='sensor')
    {
        ProcessNodeSensor(nodeId);
    }
}

/******/

function attachDetailEventListeners() {
    console.log("attachDetailEventListeners: Đang gắn lại các trình xử lý sự kiện cho nội dung chi tiết.");

    };

/******/

/** **/

//////////////////////////////////////////////////////////////////////////////////////
 $(function () {

      // ====================================================================
      // KHỞI TẠO TREE
      // ====================================================================
    // Khởi tạo jsTree
     const treeData = JSON.parse($('#tree-data').text());

      $('#main-tree').jstree({
          'core': {
              'data': treeData,
              "check_callback": true // Cho phép các thao tác như kéo thả, sửa
          },
          "plugins": ["dnd", "state", "types", "contextmenu", "wholerow"], // Kích hoạt các plugin cần thiết

          "types": {

              "sensor": {
                  "icon": false // <-- RẤT QUAN TRỌNG: Tắt icon mặc định của jsTree cho loại sensor // để chỉ hiện ảnh trong node.text
                  },

              "raspberry_pi": {
                  "icon": false // <-- RẤT QUAN TRỌNG: Tắt icon mặc định của jsTree cho loại sensor // để chỉ hiện ảnh trong node.text
                  },

               "esp_device": {
                  "icon": false // <-- RẤT QUAN TRỌNG: Tắt icon mặc định của jsTree cho loại sensor // để chỉ hiện ảnh trong node.text
                  },
          }
      });
     
      $('#main-tree').on('select_node.jstree', function (e, data) {

          const node = data.instance.get_node(data.selected[0]);
          const nodeId = node.id;
          const nodeType = node.type;

         $('#main-tree')
            .attr('data-selected-id', nodeId)
            .attr('data-selected-type', nodeType);  // lưu thêm node type

          console.log('Selected node: ' + data.instance.get_node(data.selected[0]).text);

          let detailUrl = ''

          if (nodeType === 'raspberry_pi') {
              detailUrl = `api/raspberry_pi/${nodeId}/`;
          }
          else if (nodeType === 'esp_device') {
              detailUrl = `/api/esp_device/${nodeId}/`;

          }
          else if (nodeType === 'sensor') {
              detailUrl = `/api/sensor/${nodeId}/`;
          }

         if (detailUrl) {
              $.ajax({
                  url: detailUrl,
                  method: 'GET',
                  success: function(response){
                   
                   $('#detail-content').html(response.html);
                   
                   processDetailContent(nodeType,nodeId);
                    
                  },
                  error: function(jqXHR, textStatus, errorThrown){
                      console.error("Lỗi khi tải chi tiết thiết bị:", textStatus, errorThrown);
                      $('#detail-content').html('<p>Không thể tải chi tiết thiết bị.</p>');
                  }
              });
          } else {
              $('#detail-content').html('<p>Chọn một loại thiết bị hợp lệ để xem chi tiết.</p>');
          }

      });

      // ====================================================================
      // THÊM CODE MỚI TẠI ĐÂY ĐỂ CẬP NHẬT DỮ LIỆU CẢM BIẾN
      // ====================================================================

      // Thiết lập polling: Gọi hàm fetchLatestSensorHtmlUpdates mỗi 5 giây
      const pollingInterval = 5000; // 5000 milliseconds = 5 giây
      setInterval(fetchLatestSensorHtmlUpdates, pollingInterval);

  });

