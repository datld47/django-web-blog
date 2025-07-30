window.iot_app={

    pi_node:{
        PiAutoUpdateInterval:null,
    },


    esp_node:
    {
        EspAutoUpdateInterval:null,
        EspAutoUpdateInterval2:null,
        espCheckboxBound:false
    },
    

    sensor_node:{
        
        SensorAutoUpdateInterval:null,

        table_filter:{
            start_date:null,
            stop_date:null,
            event:null,
            column_default:null
        }

    },

    charts:{
          chartSensorInstances:{},
          chartPiInstances:{}
    },
};