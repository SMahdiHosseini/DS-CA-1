for FILE in ./inputs/*;
do
  echo "######  $FILE running started #######";

  python3.8 runner.py --input $FILE --stdout --debug

  sudo service rabbitmq-server restart

  echo "######  $FILE running ended #######";
done