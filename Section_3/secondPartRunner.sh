for FILE in ./inputs/*;
do
  echo "######  $FILE running started #######";

  python3.8 runner.py --input $FILE --stdout --debug

  echo "######  $FILE running ended #######";

  sudo service rabbitmq-server restart

done