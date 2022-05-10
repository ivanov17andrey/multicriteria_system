$(document).ready(function () {
    let list = $('#list')

    $('#addToList').click((e) => {
        let checkboxes = $('input:checked.criteria-checkbox')
        let selected = checkboxes.map(function () {
            return this.value
        }).get().join(', ')

        if (selected.length == 0) return
        checkboxes.prop('checked', false)


        list.append('<li class="list-group-item">' + '<div class="input-group">\n' +
            '  <input value="' + selected + '" disabled="true" type="text" class="form-control criteria-selected" placeholder="Recipient\'s username" aria-label="Recipient\'s username" aria-describedby="button-addon2">\n' +
            '  <button class="btn btn-outline-secondary deleteSelect" type="button">X</button>\n' +
            '</div>' + '</li>')

        $('.deleteSelect').click((e) => {
            $(e.target).parent('div').parent('li').remove()
        })

        if ($('#list').children('li').length >= 10) {
            $('#addToList').prop('disabled', true)
        }
    })


    $('#use').click((e) => {
        let selected = $('.criteria-selected').map(function () {
            return this.value
        }).get()

        let coeffInputs = $('.coeff-input')
        let coeffs = coeffInputs.map(function () {
            return this.value
        }).get().join(',')

        console.log(coeffs)

        let directions = $(".direction-input option:selected").map(function () {
            return $(this).text()
        }).get().join(',')

        $.ajax({
            type: "POST",
            url: '/get_result',
            data: JSON.stringify({
                method: Number($('input[name="method"]:checked').val()),
                groups: selected,
                coefficients: coeffs,
                directions: directions
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                console.log(data)
                $('#logs').text(data.logs_py)
                location.assign('/' + data.file)
            },
            error: function (data) {
                alert('Вы что-то сделали не так')
                console.log(data)
            },
        });
    })

    $('#downloadTemplate').click(() => {
        location.assign('/input_template.xlsx')
    })

    $('#uploadFile').click(() => {
        let formData = new FormData();
        let uploadFiles = document.getElementById('fileInput').files;
        if (uploadFiles.length === 0) return
        formData.append("file", uploadFiles[0])
        formData.append("method", Number($('input[name="method"]:checked').val()))

        $.ajax({
            type: "POST",
            url: '/upload',
            data: formData,
            dataType: 'json',
            contentType: false,
            processData: false,
            success: function (resp) {
                console.log(data)
                $('#logs').text(data.logs_py)
                location.assign('/' + resp.file)
            },
            error: function (data) {
                alert('Вы что-то сделали не так')
                console.log(data)
            },
        });
    })


});