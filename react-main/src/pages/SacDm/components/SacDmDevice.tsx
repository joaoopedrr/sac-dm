import Chart from "react-apexcharts";
import { SacDmProps } from "../../SacDm/types";
import { EmptyData } from "../../../components/EmptyData";
import React, { useCallback, useEffect, useState } from "react";
import { SacDmDefaultProps } from "../../../types";
import sacDmDefault from "../../../app/services/sacdm_default";
import styled from "styled-components";


const ButtonContainer = styled.div`
  margin-bottom: 20px;
  display: flex;
  gap: 10px; /* Espaço horizontal entre os botões */
`;

const StyledButton = styled.button`
  background-color: ${({ theme }) => theme.gray800};
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: ${({ theme }) => theme.gray900}; /* Cinza mais escuro */
  }
`;

export const SacDmDevice = ({
  deviceId,
  sacDm,
}: {
  deviceId: number | null;
  sacDm: SacDmProps[];
}) => {
  const [sacDmMean, setsacDmMean] = useState<SacDmDefaultProps>();
  const [selectedValue, setSelectedValue] = useState<string>('x'); // Estado para selecionar qual valor mostrar


  const loadSacDmDefault = useCallback(async () => {
    try {
      const response = await sacDmDefault.getSacDmDefault(1);
      console.log("Response: ", response);
      
      // TODO: Alterar para pegar o veículo selecionado
      setsacDmMean(response);
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    loadSacDmDefault();
  }, [loadSacDmDefault]);

  if (!deviceId) {
    return null;
  }
  // TODO fazer a leitura correta dos dados do status
  // Função para verificar o status dos dados com base em sacDmMean.status
  const checkDataStatus = () => {
    //return sacDmMean?.status === "Ok" ? "Ok" : "Falha";
    return "Ok"
  };

  const optionsChart = {
    chart: {
      id: "device-metrics",
    },
    xaxis: {
      categories: sacDm.map((item: SacDmProps) => item.timestamp),
      labels: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        formatter: (value: number) => (value ? value.toFixed(8) : "0.00000000"),
        style: {
          colors: ["#E0E0E0"],
        },
      },
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: (value: number) => (value ? value.toFixed(8) : "0.00000000"),
      },
    },
    legend: {
      labels: {
        colors: ["E0E0E0", "E0E0E0", "E0E0E0", "E0E0E0"],
      },
    },
  };

  
  // Variáveis que variam a amostragem na tabela
  var valores = sacDm.map((item) => parseFloat(item.x_value.toFixed(8)));
  var medias = Array(sacDm.length).fill(sacDmMean?.x_mean ?? 0);
  var desvioPadraoSuperior = sacDmMean
    ? Array(sacDm.length).fill(sacDmMean.x_mean + sacDmMean.x_standard_deviation)
    : [];
  var desvioPadraoInferior = sacDmMean
    ? Array(sacDm.length).fill(sacDmMean.x_mean - sacDmMean.x_standard_deviation)
    : [];

    // Atualiza os arrays de acordo com o valor selecionado
  const getDataForSelectedValue = () => {
    switch (selectedValue) {
      case 'x':
        valores = sacDm.map((item) => parseFloat(item.x_value.toFixed(8)));
        medias = Array(sacDm.length).fill(sacDmMean?.x_mean ?? 0);
        desvioPadraoSuperior = sacDmMean
          ? Array(sacDm.length).fill(sacDmMean.x_mean + sacDmMean.x_standard_deviation)
          : [];
        desvioPadraoInferior = sacDmMean
          ? Array(sacDm.length).fill(sacDmMean.x_mean - sacDmMean.x_standard_deviation)
          : [];
          return ;
      case 'y':
        valores = sacDm.map((item) => parseFloat(item.y_value.toFixed(8)));
        medias = Array(sacDm.length).fill(sacDmMean?.y_mean ?? 0);
        desvioPadraoSuperior = sacDmMean
          ? Array(sacDm.length).fill(sacDmMean.y_mean + sacDmMean.y_standard_deviation)
          : [];
        desvioPadraoInferior = sacDmMean
          ? Array(sacDm.length).fill(sacDmMean.y_mean - sacDmMean.y_standard_deviation)
          : [];
          return ;
      case 'z':
        valores = sacDm.map((item) => parseFloat(item.z_value.toFixed(8)));
        medias = Array(sacDm.length).fill(sacDmMean?.z_mean ?? 0);
        desvioPadraoSuperior = sacDmMean
          ? Array(sacDm.length).fill(sacDmMean.z_mean + sacDmMean.z_standard_deviation)
          : [];
        desvioPadraoInferior = sacDmMean
          ? Array(sacDm.length).fill(sacDmMean.z_mean - sacDmMean.z_standard_deviation)
          : [];
        return ;
      default:
        return [];
    }
  };

  getDataForSelectedValue();

  const seriesChart = [
    
    {
      name: "Valor",
      data: valores,
    },
    {
      name: "Média",
      data: medias,
    },
    {
      name: "Desvio Padrão Superior",
      data: desvioPadraoSuperior,
    },
    {
      name: "Desvio Padrão Inferior",
      data: desvioPadraoInferior,
    },
  ];

  return (
    <div style={{ zIndex: 0, position: "relative" }}>
      {/* Retângulo com status de dados */}
      <div
        style={{
          //TODO também está ligado a utilização correta do status, mudar o valor do "Ok" abaixo caso não seja esse o passado pela variável
          backgroundColor: checkDataStatus() === "Ok" ? "#4CAF50" : "#F44336",
          color: "white",
          padding: "10px",
          textAlign: "center",
          borderRadius: "5px",
          marginBottom: "15px",
        }}
      >
        {checkDataStatus()}
      </div>

      <ButtonContainer>
        <StyledButton onClick={() => setSelectedValue("x")}>Eixo X</StyledButton>
        <StyledButton onClick={() => setSelectedValue("y")}>Eixo Y</StyledButton>
        <StyledButton onClick={() => setSelectedValue("z")}>Eixo Z</StyledButton>
      </ButtonContainer>
        
      <Chart
        options={optionsChart}
        series={seriesChart}
        type="line"
        height="350"
      />
      {sacDm.length === 0 && (
        <EmptyData message="Nenhum dado encontrado para o dispositivo selecionado" />
      )}
    </div>
  );
};

export default React.memo(SacDmDevice, (prevProps, nextProps) => {
  return (
    prevProps.deviceId === nextProps.deviceId &&
    JSON.stringify(prevProps.sacDm) === JSON.stringify(nextProps.sacDm)
  );
});

