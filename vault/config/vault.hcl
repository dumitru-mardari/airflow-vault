# enable vault UI in 127.0.0.1:8200
ui=true
# disables locking of specific segments of memory
disable_mlock = true
# api address for retrieving secrets
api_addr      = "https://127.0.0.1:8200"
# address of vault cluster
cluster_addr  = "https://127.0.0.1:8201"

# storage path for backend
storage "file" {
  path="/vault/file"
  }

# HTTP listener for requests on port 8200. tls can be enabled by providing necessary files and changing tls_disable = 0.
listener "tcp" {
  address="0.0.0.0:8200"
  tls_disable = 1
  #tls_cert_file = "/opt/vault/tls/vault-cert.pem"
  #tls_key_file = "/opt/vault/tls/vault-key.pem"
  #tls_client_ca_file = "/opt/vault/tls/vault-ca.pem"
}

# HTTP listener for requests on port 8201. tls can be enabled by providing necessary files and changing tls_disable = 0.
listener "tcp" {
  address="0.0.0.0:8201"
  tls_disable = 1
  #tls_cert_file = "/opt/vault/tls/vault-cert.pem"
  #tls_key_file = "/opt/vault/tls/vault-key.pem"
  #tls_client_ca_file = "/opt/vault/tls/vault-ca.pem"
}
