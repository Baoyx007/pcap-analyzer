$(document).ready(function() {

    $('select.dropdown').dropdown();

    $('#upload-nav').addClass('active');

    $('.ui.checkbox').checkbox();
//实现Select City
    var s={"Shanghai":[121,31],"Nanjing":[118,32]};
    function cityToStr(text){
        var arry_ll=s[text].toString().split(',');
        $("#cityMessage").html("City:"+text+", longitude="+arry_ll[0]+", latitude="+arry_ll[1]);
    }
    var text=$("#searchCity").find("option:selected").text();
        cityToStr(text);
    $("#searchCity").change(function(){
        text=$("#searchCity").find("option:selected").text();
        cityToStr(text);
    });
//Select City结束

    $('#delete-button').on('click', function(){
        $('.small.del.modal').modal({
            closable  : true,
            allowMultiple: false,
            onDeny    : function(){
                return true;
            },
            onApprove : function() {
                var delCheckbox = $("input[name='checkoption']:checked");
                var size = delCheckbox.size();
                if(size > 0){  
                    var params = "";  
                    for(var i=0;i<size;i++){
                        params+=delCheckbox.eq(i).val();
                        if (i != size-1){params=params+','};
                        }
                    $.post("delete/"+params,'',function(d){  
                            history.go(0);
                        },'text');
                    } 
            }
        }).modal('show');
    });

    $('#download-button').on('click', function(){
        var delCheckbox = $("input[name='checkoption']:checked");
        var size = delCheckbox.size();
        if(size > 0){  
            var params = "";  
            for(var i=0;i<size;i++){
                param=delCheckbox.eq(i).val();
                window.open('/download/'+param);
                }
        }
    });

    $('#analyze-button').on('click', function(){
        var delCheckbox = $("input[name='checkoption']:checked");
        var size = delCheckbox.size();
        var arry_ll=s[text].toString().split(',');
        if(size > 0){  
            var params = "";  
            for(var i=0;i<size;i++){
                param=delCheckbox.eq(i).val();
                window.open('/analyze/'+param+'?longitude='+arry_ll[0]+'&latitude='+arry_ll[1]);
                }
        }
    });
     $('#send_gen_2').on('click', function(){
        var delCheckbox = $("input[name='checkoption']:checked");
        var size = delCheckbox.size();
        var arry_ll=s[text].toString().split(',');
        if(size > 0){
            var params = "";
            for(var i=0;i<size;i++){
                param=delCheckbox.eq(i).val();
                window.open('/autogen_2/'+param);
                }
        }
        });


    $('#fileupload').fileupload({
        url: '/upload',
        add: function (e, data) {
            var goUpload = true;
            var uploadFile = data.files[0];
            if (!(/\.(pcap)$/i).test(uploadFile.name)) {
                alert('Pcap file only!');
                goUpload = false;
            }
            if (uploadFile.size > 30000000) { // 2mb
                alert('Max Size is 30 MB!');
                goUpload = false;
            }
            if (goUpload == true) {
                data.submit();
            }
        },
        progressall: function (e, data) {
            $('.progress').progress({percent:1});
            var progressbar = parseInt(data.loaded / data.total * 100, 10);
            console.log(progressbar);
            $('.progress').progress({percent:progressbar});
        },
        done: function (e, data) {
            if (data['textStatus']=="success")
                $("#progresslabel").append("Upload OK!");
                $('#fileupload').attr({"disabled":"disabled"});
                $('.small.ok.modal').modal('show');
                history.go(0);
        },
    });

//添加手机设备信息
   $('#addDevice-button').on('click', function(){
       $('#addDevice-ok').modal({
            closable  : true,
            allowMultiple: false,
            onDeny    : function(){
                return true;
            },
            onApprove : function() {
                alert("submit");
            }
        }).modal('show');
    });

});
