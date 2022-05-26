$(document).ready(function () {
    var list = $('#list')

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
        let cNames = $('.criteria-names input').map(function () {
            return this.value
        }).get()
        console.log(cNames)
        if (cNames.some((v) => v == '')) {
            alert('Названия критериев должны быть заполнены')
        }

        let aNames = $('.alternative-name textarea').map(function () {
            return $(this).val()
        }).get()
        console.log(aNames)
        if (aNames.some((v) => v == '')) {
            alert('Названия альтернатив должны быть заполнены')
        }

        $('.criteria-values').each(function () {
            el = $(this)
            data = el.data()
            tableData.data[data.row][data.col] = el.children().val()
        })
        console.log(tableData.data)

        if (tableData.data.flat().some((v) => v == '' || Number(v) <= 0)) {
            alert('Значения критериев должны быть выбраны и не могу быть <= 0')
        }

        let selected = $('.criteria-selected').map(function () {
            return this.value.replaceAll(' ', '').replaceAll(',', ';')
        }).get()
        console.log(selected)

        let coeffInputs = $('.coeff-input')
        let coeffs = coeffInputs.map(function () {
            return this.value
        }).get()
        console.log(coeffs)

        let directions = $(".direction-input option:selected").map(function () {
            return $(this).text()
        }).get()
        console.log(directions)

        $.ajax({
            type: "POST",
            url: '/get_result',
            data: JSON.stringify({
                method: Number($('input[name="method"]:checked').val()),
                alternatives_names: aNames.join('|'),
                criteria_names: cNames.join('|'),
                estimates: tableData.data.map(g => g.join(';')).join('|'),
                coefficients: coeffs.join('|'),
                directions: directions.join('|'),
                groups: selected.join('|'),
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                console.log(data)
                $('#logs').text(data.logs_py)
                $('.collapse').addClass('show')
                $('#retry').removeClass('d-none')
                document.getElementById('result').scrollIntoView({
                    behavior: 'smooth'
                })
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
            success: function (data) {
                console.log(data)
                $('#logs').text(data.logs_py)
                $('.collapse').addClass('show')
                $('#retry').removeClass('d-none')
                document.getElementById('result').scrollIntoView({
                    behavior: 'smooth'
                })
                location.assign('/' + data.file)
            },
            error: function (data) {
                alert('Вы что-то сделали не так')
                console.log(data)
            },
        });
    })

    function NArray(row, cols) {
        const arr = []
        for (let i = 0; i < row; i++) {
            arr.push(Array(cols).fill(null))
        }
        return arr
    }

    var n = 30
    var m = 9
    var tableData = {
        alternativesNum: n,
        criteriaNum: m,
        data: NArray(n, m)
    }

    $('#alt-num').val(tableData.alternativesNum)
    $('#crit-num').val(tableData.criteriaNum)

    console.log(tableData)

    $('#create-table').click((e) => {
        list.children().remove()
        n = $('#alt-num').val()
        m = $('#crit-num').val()

        tableData.alternativesNum = n
        tableData.criteriaNum = m
        tableData.data = NArray(n, m)

        const tableWrapper = $('#estimates-table')
        tableWrapper.children().remove()

        const tableTemplate = $(`
        <table class="table table-bordered">
            <thead>
            <tr class="criteria-nums">
              <th></th>
              <th></th>
            </tr>
            <tr class="criteria-row">
              <th>#</th>
              <th>Название</th>
            </tr>
            </thead>
            
            <tbody>
            </tbody>
          </table>
        `)

        tableWrapper.append(tableTemplate)

        for (let i = 0; i < tableData.criteriaNum; i++) {
            $('.criteria-nums').append(`<th>K${i + 1}</th>`)
            cName = $(`<th><input type="text" class="table-input"></th>`)
            cName.addClass(`criteria-names`)
            cName.data('num', i)
            $('.criteria-row').append(cName)
        }

        for (let j = 0; j < tableData.alternativesNum; j++) {
            tRow = $(`<tr class="alternative-row"></tr>`)
            tableTemplate.find('tbody').append(tRow)
            tRow.append(`<th>A${j + 1}</th>`)
            tRow.append(`<td class="alternative-name"><textarea class="table-input-text"></textarea></td>`)

            for (let i = 0; i < tableData.criteriaNum; i++) {
                cValue = $(`<td><input type="number" min="1" class="table-input"></td>`)
                cValue.addClass(`criteria-values`)
                cValue.data('row', j)
                cValue.data('col', i)
                tRow.append(cValue)
            }
        }

        const criteriaTableWrapper = $('#criteria-table')
        criteriaTableWrapper.children().remove()

        const criteriaTableTemplate = $(`
        <table class="table table-bordered">
            <tbody>
            <tr class="criteria-checkboxes">
              <th></th>
            </tr>
            <tr class="criteria-coeffs">
              <th>Коэффициент</th>
            </tr>
            <tr class="criteria-direction">
              <th></th>
            </tr>
            </tbody>
          </table>
        `)

        criteriaTableWrapper.append(criteriaTableTemplate)

        for (let i = 0; i < tableData.criteriaNum; i++) {
            $('.criteria-checkboxes').append(`
                <th>
                  <div class="form-check form-check-inline">
                    <input class="criteria-checkbox form-check-input" type="checkbox" id="inlineCheckbox${i}" value="K${i+1}">
                    <label class="form-check-label" for="inlineCheckbox${i}">K${i+1}</label>
                  </div>
                </th>
            `)

            $('.criteria-coeffs').append(`<th><input type="number" min="1" value="1" class="form-control coeff-input"></th>`)

            $('.criteria-direction').append(`
                <th>
                  <select class="direction-input form-control">
                    <% if c[:direction] == 'max' %>
                      <option selected>max</option>
                      <option>min</option>
                  </select>
                </th>
            `)
        }

    })

    $('#change-method').click(() => document.getElementById('select-method').scrollIntoView({behavior: 'smooth'}))
    $('#change-nums').click(() => document.getElementById('select-nums').scrollIntoView({behavior: 'smooth'}))
    $('#change-estimates').click(() => document.getElementById('estimates-table').scrollIntoView({behavior: 'smooth'}))
    $('#change-coeffs').click(() => document.getElementById('select-groups').scrollIntoView({behavior: 'smooth'}))

});