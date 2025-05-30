def levenshtein(texto1, texto2):
    n = len(texto1)
    m = len(texto2)

    matriz = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        matriz[i][0] = i

    for j in range(m + 1):
        matriz[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if texto1[i - 1] == texto2[j - 1]:
                custo = 0
            else:
                custo = 1

            matriz[i][j] = min(
                matriz[i - 1][j] + 1,      # remoção
                matriz[i][j - 1] + 1,      # inserção
                matriz[i - 1][j - 1] + custo  # substituição
            )

    return matriz[n][m]

print(levenshtein('cachorro', 'gato'))