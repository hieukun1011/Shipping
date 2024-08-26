/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";
$(document).ready(function() {
    const jsonExams = $('#exams_data').val();
    let exams;
    let filteredExams = [];
    const examsPerPage = 8;
    let currentPage = 1;

    if (jsonExams) {
        const jsonStringExams = jsonExams.replace(/'/g, '"').replace(/False/g, 'null');
        exams = JSON.parse(jsonStringExams);
        filteredExams = [...exams];

        function displayExams() {
            const start = (currentPage - 1) * examsPerPage;
            const end = start + examsPerPage;
            const paginatedExams = filteredExams.slice(start, end);
            $('#exam-container').empty();
            paginatedExams.forEach(exam => {
                const examCard = `
                    <div class="col-md-6 col-sm-6 p-2 exam-item">
                        <div class="feature" style="border-radius:10px;box-shadow: 0 8px 10px rgba(0, 0, 0, .15)">
                            <div class="card-body" style="background-color:#E8EBF4 !important;">
                                <div class="exam-name" style="color:#595A80">${exam.name}</div>
                            </div>
                            <div class="card card-body bg-primary-light well1 mb-4" style="border-radius: unset;">
                                <div class="feature-content-box">
                                    <div class="d-flex" style="justify-content: space-between;">
                                        <div class="d-grid">
                                            <div class="d-grid">
                                                    <span style="color:#9B9D9D;font-weight:500">Tên chuyên mục</span>
                                                    <p style="overflow: hidden;">
                                                        ${exam.categ_id ? exam.categ_id : ''}
                                                    </p>
                                            </div>
                                            <div class="d-grid">
                                               <span style="color:#9B9D9D;font-weight:500">Loại</span>
                                                 <p style="overflow: hidden;">
                                                    ${exam.type ? exam.type : ''}
                                                </p>
                                           </div>
                                       </div>
                                        <div>${exam.no_of_attempt == exam.quiz_attempt['ttl_atmp'] && exam.quiz_attempt['ttl_atmp'] != 0 ? `Score: <span>${exam.quiz_attempt['ttl_atmp']}</span>` : `Attempt: <span>${quiz_attempt[exam.id].ttl_atmp}</span>`}</div>
                                    </div>
                                    <div style="${exam.description ? 'height: 75px;' : ''}">
                                        <p style="${exam.description ? 'height: 75px;overflow: hidden' : ''}">
                                            ${exam.description ? exam.description : ''}
                                        </p>
                                    </div>
                                    <hr/>
                                    <div class="d-flex col-xl-12" style="align-items: center;justify-content: space-between;" ${exam.quiz_attempt['allow'] == 1 ? '' : 'hidden'}>
                                        <div class="col-6">
                                            <div class="d-flex">
                                                <div style="color:#9B9D9D;font-weight:500">Avg Result :</div>
                                                <div class="d-flex" style="margin-left:4%">
                                                    <span style="color:#9DCDEA;font-weight:500">${exam.quiz_attempt['avg_res']}</span>
                                                    <div style="color:#9DCDEA;font-weight:500">%</div>
                                                </div>
                                            </div>
                                        </div>
                                       <div>
                                            <a class="btn" style="text-transform: uppercase;background-color:#F9B600;font-weight:500" href="/exam/start/${exam.id}">
                                                Bắt đầu bài kiểm tra
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $('#exam-container').append(examCard);
            });
        }

        function displayPagination() {
            const pageCount = Math.ceil(filteredExams.length / examsPerPage);
            $('#pagination-controls').empty();

            const prevLink = $('<a>')
                .text('«')
                .addClass('pagination-link prev')
                .attr('href', '#');

            if (currentPage === 1) {
                prevLink.addClass('disabled');
            }

            prevLink.on('click', function(event) {
                event.preventDefault();
                if (currentPage > 1) {
                    currentPage--;
                    displayExams();
                    displayPagination();
                }
            });

            $('#pagination-controls').append(prevLink);

            for (let i = 1; i <= pageCount; i++) {
                const pageLink = $('<a>')
                    .text(i)
                    .addClass('pagination-link')
                    .data('page', i)
                    .attr('href', '#');

                if (i === currentPage) {
                    pageLink.addClass('active');
                }

                pageLink.on('click', function(event) {
                    event.preventDefault();
                    currentPage = $(this).data('page');
                    displayExams();
                    displayPagination();
                });

                $('#pagination-controls').append(pageLink);
            }

            const nextLink = $('<a>')
                .text('»')
                .addClass('pagination-link next')
                .attr('href', '#');

            if (currentPage === pageCount) {
                nextLink.addClass('disabled');
            }

            nextLink.on('click', function(event) {
                event.preventDefault();
                if (currentPage < pageCount) {
                    currentPage++;
                    displayExams();
                    displayPagination();
                }
            });

            $('#pagination-controls').append(nextLink);
        }

        function searchButton() {
            var keyword = document.getElementById('searchKeyword').value.toLowerCase();
            filteredExams = exams.filter(function(exam) {
                var examName = exam.name.toLowerCase();
                return examName.includes(keyword);
            });

            currentPage = 1;

            displayExams();
            displayPagination();
        }

        displayExams();
        displayPagination();

        $('#searchButton').on('click', searchButton);
    }
});
