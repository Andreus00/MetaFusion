npx hardhat node &

sleep 3

npx hardhat run scripts/deploy_metafusion.ts --network localhost

sleep 3

python3 -m src.tracker.tracker &

sleep 3

python3 -m src.oracle.oracle &

sleep 20

collection=1 npx hardhat run scripts/create_collection.ts --network localhost

uvicorn src.web_api.main:app  --reload --host 0.0.0.0 --port 3000







