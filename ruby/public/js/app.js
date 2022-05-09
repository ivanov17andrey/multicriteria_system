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

        $.ajax({
            type: "POST",
            url: '/get_table',
            data: JSON.stringify({groups: selected, coefficients: coeffs}),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                location.assign('/' + data.file)
            },
            error: function (data) {
                console.log(data)
            },
        });
    })
});