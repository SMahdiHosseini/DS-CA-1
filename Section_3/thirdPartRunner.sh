for FILE in ./inputs/*;
do
  echo "######  $FILE running started #######";

  A="$(cut -d'/' -f3 <<<"$FILE")"

  python3.8 runner.py --input $FILE --configs ./configs/$A.conf --stdout --debug

  echo "######  $FILE running ended #######";

  sudo service rabbitmq-server restart

done