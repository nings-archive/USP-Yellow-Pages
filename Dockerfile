FROM easypi/alpine-arm

RUN apk update
RUN apk add python3
RUN pip3 install python-telegram-bot

RUN apk add tzdata
RUN cp /usr/share/zoneinfo/Asia/Singapore /etc/localtime
RUN echo "Asia/Singapore" > /etc/timezone

RUN mkdir "/USP Yellow Pages"
WORKDIR "/USP Yellow Pages"
COPY ./uyp_bot/* ./uyp_bot/

CMD python3 uyp_bot
