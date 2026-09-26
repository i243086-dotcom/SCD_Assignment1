#!/usr/bin/env sh
set -eu

for cmd in docker kind kubectl kustomize envsubst; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "Missing required command: $cmd" >&2; exit 1; }
done

CLUSTER_NAME="${CLUSTER_NAME:-civicpulse}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-civicpulse_local_only}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://civicpulse:${POSTGRES_PASSWORD}@postgres:5432/civicpulse}"
export GROQ_API_KEY="${GROQ_API_KEY:-}"
export TRIAGE_PROVIDER="${TRIAGE_PROVIDER:-simulated}"

if ! kind get clusters | grep -qx "$CLUSTER_NAME"; then
  kind create cluster --name "$CLUSTER_NAME" --config scripts/kind-config.yaml --image kindest/node:v1.32.2
fi

echo "Building local images..."
docker build -t civicpulse-backend:dev backend
docker build -t civicpulse-frontend:dev frontend
kind load docker-image --name "$CLUSTER_NAME" civicpulse-backend:dev civicpulse-frontend:dev

echo "Installing ingress-nginx and metrics-server..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/kind/deploy.yaml
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.7.2/components.yaml
kubectl -n kube-system patch deployment metrics-server --type=json -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]' || true

if ! kubectl get crd verticalpodautoscalers.autoscaling.k8s.io >/dev/null 2>&1; then
  echo "Installing VPA components (pinned release)..."
  tmpdir="$(mktemp -d)"
  git clone --quiet --depth 1 --branch vertical-pod-autoscaler-1.2.0 https://github.com/kubernetes/autoscaler.git "$tmpdir/autoscaler"
  "$tmpdir/autoscaler/vertical-pod-autoscaler/hack/vpa-up.sh"
  rm -rf "$tmpdir"
fi

rendered="$(mktemp)"
kustomize build k8s/overlays/dev | envsubst > "$rendered"
kubectl apply -f "$rendered"
rm -f "$rendered"

kubectl wait -n civicpulse --for=condition=complete job/civicpulse-migrate --timeout=180s
kubectl rollout status -n civicpulse statefulset/postgres --timeout=180s
kubectl rollout status -n civicpulse deployment/redis --timeout=180s
kubectl rollout status -n civicpulse deployment/backend --timeout=180s
kubectl rollout status -n civicpulse deployment/frontend --timeout=180s

echo "CivicPulse is available through the Ingress at http://civicpulse.local"
echo "Add '127.0.0.1 civicpulse.local' to your hosts file if DNS does not resolve it."
